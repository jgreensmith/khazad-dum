from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from importlib import resources
from pathlib import Path


TF_HOME = Path.home() / ".khazad-dum" / "terraform"
KEYS_DIR = TF_HOME / "keys"
BUNDLES_DIR = TF_HOME / "bundles"
SERVERS_TFVARS = TF_HOME / "servers.auto.tfvars.json"

# Control port the listener binds on every endpoint (reached over Twingate).
LISTENER_PORT = 8080

# Must mirror the provider/module blocks in terraform/main.tf.
SUPPORTED_REGIONS = (
    "us-east-1",
    "us-east-2",
    "us-west-2",
    "eu-west-1",
    "eu-west-2",
    "eu-central-1",
)
DEFAULT_INSTANCE_TYPE = "t3.micro"

OP_ACCESS_KEY_REF = "op://Private/AWS_CLI/access_key_id"
OP_SECRET_KEY_REF = "op://Private/AWS_CLI/secret_access_key"

# Twingate settings, injected as TF_VAR_* for the provider, the connector
# user_data, and the homelab resource. A pre-set TF_VAR_* in the environment
# wins, so these 1Password items are only read when not already provided.
OP_TG_API_TOKEN_REF = "op://Private/Twingate/api_token"
OP_TG_NETWORK_REF = "op://Private/Twingate/network"
OP_TG_HOMELAB_NETWORK_REF = "op://Private/Twingate/homelab_remote_network"


def _copy_tree(src, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for entry in src.iterdir():
        target = dst / entry.name
        if entry.is_dir():
            _copy_tree(entry, target)
        else:
            target.write_bytes(entry.read_bytes())


def ensure_tf_home() -> None:
    """Sync the packaged terraform skeleton into the writable TF home.

    Refreshes the .tf/.gitignore files but never touches the CLI-managed
    servers.auto.tfvars.json, generated keys, or terraform state.
    """
    KEYS_DIR.mkdir(parents=True, exist_ok=True)
    skeleton = resources.files("khazad_dum") / "terraform"
    _copy_tree(skeleton, TF_HOME)


def load_servers() -> dict:
    if SERVERS_TFVARS.exists():
        data = json.loads(SERVERS_TFVARS.read_text())
    else:
        data = {}
    data.setdefault("servers", {})
    data["keys_dir"] = str(KEYS_DIR)
    return data


def save_servers(data: dict) -> None:
    SERVERS_TFVARS.parent.mkdir(parents=True, exist_ok=True)
    SERVERS_TFVARS.write_text(json.dumps(data, indent=2) + "\n")


def generate_ssh_keys(experiment: str) -> Path:
    key_dir = KEYS_DIR / experiment
    private_key = key_dir / "id_rsa"
    if private_key.exists():
        return private_key
    key_dir.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["ssh-keygen", "-t", "rsa", "-b", "4096", "-N", "", "-q",
             "-C", f"khazad-dum-{experiment}", "-f", str(private_key)],
            check=True,
        )
    except FileNotFoundError:
        sys.exit("ssh-keygen not found. Install OpenSSH to generate experiment keys.")
    except subprocess.CalledProcessError as exc:
        sys.exit(f"ssh-keygen failed (exit {exc.returncode}).")
    return private_key


def _op_read(ref: str) -> str:
    try:
        result = subprocess.run(
            ["op", "read", ref], capture_output=True, text=True, check=True
        )
    except FileNotFoundError:
        sys.exit("1Password CLI (`op`) not found. Install it to load AWS credentials.")
    except subprocess.CalledProcessError as exc:
        sys.exit(f"`op read {ref}` failed: {exc.stderr.strip() or exc.returncode}")
    return result.stdout.strip()


def _set_var_default(env: dict[str, str], key: str, op_ref: str) -> None:
    """Set env[key] from 1Password unless the caller already provided it."""
    if not env.get(key):
        env[key] = _op_read(op_ref)


def tf_env() -> dict[str, str]:
    """os.environ with AWS creds + Twingate TF_VARs injected from 1Password.

    AWS creds feed the provider and the MinIO/S3 backend. The ``TF_VAR_tg_*``
    values feed the Twingate provider, the connector user_data, and the homelab
    resource. Any ``TF_VAR_*`` already set in the environment is left untouched,
    so a user can bypass 1Password by exporting them directly.
    """
    env = os.environ.copy()
    env["AWS_ACCESS_KEY_ID"] = _op_read(OP_ACCESS_KEY_REF)
    env["AWS_SECRET_ACCESS_KEY"] = _op_read(OP_SECRET_KEY_REF)
    _set_var_default(env, "TF_VAR_tg_api_token", OP_TG_API_TOKEN_REF)
    _set_var_default(env, "TF_VAR_tg_network", OP_TG_NETWORK_REF)
    _set_var_default(env, "TF_VAR_tg_homelab_remote_network", OP_TG_HOMELAB_NETWORK_REF)
    return env


def _terraform(args: list[str], env: dict[str, str]) -> int:
    try:
        return subprocess.run(["terraform", *args], cwd=TF_HOME, env=env).returncode
    except FileNotFoundError:
        sys.exit("terraform not found. Install Terraform (>= 1.6) to manage experiments.")


def init(env: dict[str, str]) -> None:
    if _terraform(["init", "-input=false"], env) != 0:
        sys.exit("terraform init failed.")


def apply(env: dict[str, str]) -> None:
    if _terraform(["apply", "-auto-approve", "-input=false"], env) != 0:
        sys.exit("terraform apply failed.")


def _output_json(name: str, env: dict[str, str]) -> dict:
    try:
        result = subprocess.run(
            ["terraform", "output", "-json", name],
            cwd=TF_HOME, env=env, capture_output=True, text=True,
        )
    except FileNotFoundError:
        sys.exit("terraform not found.")
    if result.returncode != 0 or not result.stdout.strip():
        return {}
    return json.loads(result.stdout)


def output_servers(env: dict[str, str]) -> dict:
    """AWS endpoints (with public_ip/dns) for the build-time SSH summary."""
    return _output_json("servers", env)


def output_endpoints(env: dict[str, str]) -> dict:
    """All endpoints (AWS + homelab) the control plane reaches over Twingate.

    Each value has at least {name, experiment, target, role, address,
    listener_port}; ``address`` is what khazad-dum dials over the tunnel.
    """
    return _output_json("endpoints", env)


def stage_bundle(
    experiment: str,
    name: str,
    payload_dir: Path,
    listener_text: str,
    bootstrap_text: str,
) -> Path:
    """Assemble a per-endpoint provisioning bundle under the TF home.

    The bundle is the directory Terraform delivers to the host/container:
    ``server.py`` (the fixed listener), ``payload/`` (the project's experiment
    code), and a generated ``bootstrap.sh``. Returns the bundle directory.
    """
    bundle = BUNDLES_DIR / f"{experiment}__{name}"
    if bundle.exists():
        shutil.rmtree(bundle)
    bundle.mkdir(parents=True, exist_ok=True)
    (bundle / "server.py").write_text(listener_text)
    _copy_tree(payload_dir, bundle / "payload")
    bootstrap = bundle / "bootstrap.sh"
    bootstrap.write_text(bootstrap_text)
    bootstrap.chmod(0o755)
    return bundle
