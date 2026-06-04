from __future__ import annotations

import argparse
import io
import json
import shutil
import sys
import tarfile
import time
import urllib.error
import urllib.request
from importlib import resources
from pathlib import Path

from . import claude_sdk
from . import terraform as tf
from .state import State, STATE_DIR_NAME
from .steps import STEPS, Step, get_step
from .tokens import assert_within_limit, count_tokens, MAX_TOKENS


DOCS_DIR = "documentation"
NOTES_PROJECTS_DIR = Path.home() / "Notes" / "Projects"

EXPERIMENT_DIR = "02_experiment"
SERVERS_JSON_NAME = "servers.json"
RESULTS_DIR_NAME = "results"  # under documentation/02_experiment/process/

# Step 02 has two human-owned input docs (not a single scope.md); the gate
# challenges both, and they are injected into every step-02 prompt as labelled
# sections. The agent keeps them pristine and refines copies under process/.
EXPERIMENT_INPUT_DOCS = {
    "project-description.md": "Project Description",
    "experiment-plan.md": "Experiment Plan",
}

def _template_text(relative: str) -> str:
    return (resources.files("khazad_dum.workflows") / relative).read_text()


def _project_root() -> Path:
    return Path.cwd()


def _docs_root(project_root: Path) -> Path:
    return project_root / DOCS_DIR


def _is_initialised(project_root: Path) -> bool:
    return (project_root / STATE_DIR_NAME).exists() and _docs_root(project_root).exists()


def _require_init(project_root: Path) -> None:
    if not _is_initialised(project_root):
        sys.exit("khazad-dum is not initialised here. Run `khazad-dum init` first.")


def cmd_init(args: argparse.Namespace) -> None:
    project_root = _project_root()
    docs = _docs_root(project_root)

    if docs.exists() and not docs.is_symlink() and any(docs.iterdir()):
        if not args.force:
            sys.exit(f"{docs} already exists and is not empty. Use --force to proceed.")

    docs.mkdir(parents=True, exist_ok=True)

    for step in STEPS:
        step_dir = docs / step.dir_name
        (step_dir / "input").mkdir(parents=True, exist_ok=True)
        (step_dir / "process").mkdir(parents=True, exist_ok=True)
        (step_dir / "output").mkdir(parents=True, exist_ok=True)
        if step.dir_name == EXPERIMENT_DIR:
            _seed_experiment_inputs(step_dir)
            continue
        scope_path = step_dir / "input" / "scope.md"
        if not scope_path.exists():
            try:
                scope_template = _template_text(step.scope_template_path)
            except (FileNotFoundError, OSError):
                # Some later phases have no scope template yet — seed a
                # placeholder rather than aborting the whole init.
                scope_template = "<!-- scope template not yet defined for this step -->"
            scope_path.write_text(f"# {step.name} — Scope\n\n{scope_template}")

    # No servers.json / payload is seeded: the experiment draft step authors them
    # under process/, and build reads them from there (no human promotion).

    (project_root / STATE_DIR_NAME).mkdir(exist_ok=True)
    State.load(project_root).save(project_root)

    _create_notes_symlink(project_root, docs)

    print(f"Initialised khazad-dum in {project_root}")
    print(f"  documentation/  ({len(STEPS)} steps)")
    print(f"  {DOCS_DIR}/{EXPERIMENT_DIR}/input/  (project-description.md + experiment-plan.md)")
    print(f"  {STATE_DIR_NAME}/state.json")


def _create_notes_symlink(project_root: Path, docs: Path) -> None:
    if not NOTES_PROJECTS_DIR.exists():
        print(f"  (skipped symlink: {NOTES_PROJECTS_DIR} does not exist)")
        return
    link = NOTES_PROJECTS_DIR / project_root.name
    if link.exists() or link.is_symlink():
        if link.is_symlink() and link.resolve() == docs.resolve():
            print(f"  symlink already in place: {link} -> {docs}")
            return
        print(f"  (skipped symlink: {link} already exists)")
        return
    link.symlink_to(docs, target_is_directory=True)
    print(f"  linked {link} -> {docs}")


def cmd_status(args: argparse.Namespace) -> None:
    project_root = _project_root()
    if not _is_initialised(project_root):
        print("khazad-dum is not initialised here. Run `khazad-dum init`.")
        return
    state = State.load(project_root)
    print(f"Project: {project_root}")
    print("Steps:")
    for step in STEPS:
        if step.dir_name in state.completed:
            marker = "[x]"
        elif state.current == step.dir_name:
            marker = "[~]"
        else:
            marker = "[ ]"
        print(f"  {marker} {step.index}. {step.name}  ({step.dir_name})")
        if step.sub_prompts:
            done_subs = state.sub_completed.get(step.dir_name, [])
            for sub in step.sub_prompts:
                sub_marker = "[x]" if sub in done_subs else "[ ]"
                print(f"       {sub_marker} {sub}")
    nxt = _next_pending(state)
    if nxt:
        print(f"\nNext pending: {nxt.index}. {nxt.name}")
        print(f"Run with: khazad-dum run {nxt.slug}")
    else:
        print("\nAll steps completed.")


def _next_pending(state: State) -> Step | None:
    for step in STEPS:
        if step.dir_name not in state.completed:
            return step
    return None


# Maps a sub-prompt / analysis-prompt name → template file stems to inject.
_SUB_PROMPT_TEMPLATES: dict[str, tuple[str, ...]] = {
    # research
    "research-gate": ("questionnaire",),
    "draft-and-refine": ("literature-review", "questionnaire"),
    "complete-research-step": (),
    # experiment
    "experiment-gate": ("questionnaire",),
    "draft-experiment": ("script-doc", "questionnaire"),
    "interpret-and-refine": ("questionnaire",),
    "experiment-report": ("experiment-report",),
}


def _experiment_input_sections(project_root: Path) -> list[str]:
    """The two human-owned step-02 input docs, as labelled prompt sections."""
    input_dir = _docs_root(project_root) / EXPERIMENT_DIR / "input"
    sections: list[str] = []
    for fname, label in EXPERIMENT_INPUT_DOCS.items():
        path = input_dir / fname
        if path.exists():
            sections.append(f"---\n\n## {label}\n\n{path.read_text()}")
    return sections


def _seed_experiment_inputs(step_dir: Path) -> None:
    """Seed the two human-owned step-02 input docs from their templates."""
    for fname in EXPERIMENT_INPUT_DOCS:
        dest = step_dir / "input" / fname
        if not dest.exists():
            dest.write_text(_template_text(f"{EXPERIMENT_DIR}/templates/{fname}"))


def _build_prompt(step: Step, project_root: Path) -> str:
    prompt = _template_text(f"{step.dir_name}/prompts/prompt.md")
    scope_path = _docs_root(project_root) / step.dir_name / "input" / "scope.md"
    scope = scope_path.read_text() if scope_path.exists() else ""
    parts = [prompt]
    if scope:
        parts.append(f"---\n\n## Scope\n\n{scope}")
    return "\n\n".join(parts)


def _build_sub_prompt(step: Step, sub_prompt: str, project_root: Path) -> str:
    process = _template_text(f"{step.dir_name}/prompts/{sub_prompt}.md")
    parts = [process]
    if step.dir_name == EXPERIMENT_DIR:
        parts.extend(_experiment_input_sections(project_root))
    else:
        scope_path = _docs_root(project_root) / step.dir_name / "input" / "scope.md"
        scope = scope_path.read_text() if scope_path.exists() else ""
        if scope:
            parts.append(f"---\n\n## Project Description\n\n{scope}")
    for tname in _SUB_PROMPT_TEMPLATES.get(sub_prompt, ()):
        tmpl = _template_text(f"{step.dir_name}/templates/{tname}.md")
        parts.append(f"---\n\n## Template\n\n{tmpl}")
    return "\n\n".join(parts)


def _next_pending_sub_prompt(step: Step, state: State) -> str | None:
    done = state.sub_completed.get(step.dir_name, [])
    for sub in step.sub_prompts:
        if sub not in done:
            return sub
    return None


def _invoke(prompt: str, project_root: Path) -> claude_sdk.Result:
    """Run a step prompt through the Agent SDK in WRITE mode (full coding access).

    Exits with a clear message if the SDK or the `claude` binary is unavailable;
    SDK-level errors during the run are reported back on the Result.
    """
    try:
        return claude_sdk.run_prompt(
            prompt, mode=claude_sdk.Mode.WRITE, cwd=project_root
        )
    except claude_sdk.ClaudeUnavailable as exc:
        sys.exit(f"[khazad-dum] {exc}")


def cmd_run(args: argparse.Namespace) -> None:
    project_root = _project_root()
    _require_init(project_root)
    state = State.load(project_root)

    if args.step:
        step = get_step(args.step)
        if step is None:
            sys.exit(f"Unknown step: {args.step}")
    else:
        step = _next_pending(state)
        if step is None:
            print("All steps completed.")
            return

    if step.sub_prompts:
        sub = _next_pending_sub_prompt(step, state)
        if sub is None:
            print(f"[khazad-dum] Step {step.index} already complete.")
            return
        prompt = _build_sub_prompt(step, sub, project_root)
        tokens = assert_within_limit(prompt)
        sub_idx = list(step.sub_prompts).index(sub) + 1
        print(f"[khazad-dum] Step {step.index}: {step.name} ({sub_idx}/{len(step.sub_prompts)}): {sub}")
        print(f"[khazad-dum] Prompt size: {tokens} tokens (limit {MAX_TOKENS})")

        if args.dry_run:
            print("---\n" + prompt + "\n---")
            return

        state.current = step.dir_name
        state.save(project_root)

        result = _invoke(prompt, project_root)

        if not result.is_error:
            state.mark_sub_completed(step.dir_name, sub)
            if _next_pending_sub_prompt(step, state) is None:
                state.mark_completed(step.dir_name)
                print(f"[khazad-dum] Step {step.index} complete.")
            else:
                remaining = len(step.sub_prompts) - len(state.sub_completed.get(step.dir_name, []))
                print(f"[khazad-dum] Sub-step complete. {remaining} sub-step(s) remaining.")
            state.save(project_root)
        else:
            print(f"[khazad-dum] claude reported an error ({result.subtype or 'unknown'}). Sub-step not marked complete.")
            sys.exit(1)
        return

    prompt = _build_prompt(step, project_root)
    tokens = assert_within_limit(prompt)
    print(f"[khazad-dum] Step {step.index}: {step.name}")
    print(f"[khazad-dum] Prompt size: {tokens} tokens (limit {MAX_TOKENS})")

    if args.dry_run:
        print("---\n" + prompt + "\n---")
        return

    state.current = step.dir_name
    state.save(project_root)

    result = _invoke(prompt, project_root)

    if not result.is_error:
        state.mark_completed(step.dir_name)
        state.save(project_root)
        print(f"[khazad-dum] Step {step.index} marked complete.")
    else:
        print(f"[khazad-dum] claude reported an error ({result.subtype or 'unknown'}). Step not marked complete.")
        sys.exit(1)


def _load_experiment_servers(project_root: Path) -> list[dict]:
    path = _docs_root(project_root) / EXPERIMENT_DIR / "process" / SERVERS_JSON_NAME
    if not path.exists():
        sys.exit(
            f"No experiment config at {path}. Run the experiment gate + draft "
            f"(`khazad-dum run experiment`) to produce servers.json + payload first."
        )
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        sys.exit(f"Invalid JSON in {path}: {exc}")
    if not isinstance(data, list):
        sys.exit(f"{path} must contain a JSON array of server objects.")
    return data


def _validate_servers(servers: list[dict], project_root: Path) -> None:
    if not servers:
        sys.exit("No endpoints defined in servers.json. Add at least one endpoint object.")
    seen: set[str] = set()
    for i, s in enumerate(servers):
        if not isinstance(s, dict):
            sys.exit(f"Endpoint #{i + 1} is not an object.")
        for key in ("name", "target", "role", "payload_dir"):
            if not s.get(key):
                sys.exit(f"Endpoint #{i + 1} is missing required field '{key}'.")
        name = s["name"]
        if name in seen:
            sys.exit(f"Duplicate endpoint name '{name}'. Names must be unique within an experiment.")
        seen.add(name)

        target = s["target"]
        if target not in ("aws", "homelab"):
            sys.exit(f"Endpoint '{name}': target must be 'aws' or 'homelab', got '{target}'.")
        if target == "aws":
            if s.get("region") not in tf.SUPPORTED_REGIONS:
                sys.exit(
                    f"Endpoint '{name}' (aws) uses unsupported/missing region '{s.get('region')}'. "
                    f"Supported: {', '.join(tf.SUPPORTED_REGIONS)}."
                )
        elif not s.get("docker_image"):
            sys.exit(f"Endpoint '{name}' (homelab) is missing required field 'docker_image'.")

        payload = (project_root / s["payload_dir"]).resolve()
        if not payload.is_dir():
            sys.exit(f"Endpoint '{name}': payload_dir not found: {payload}. Re-run the experiment draft step.")
        if not (payload / "run").is_file():
            sys.exit(f"Endpoint '{name}': payload_dir has no executable 'run': {payload}. Re-run the experiment draft step.")


def _listener_source() -> str:
    """The packaged listener served standalone on each endpoint as server.py."""
    return (resources.files("khazad_dum") / "listener" / "server.py").read_text()


def _bootstrap_text(target: str, role: str, port: int) -> str:
    """Generate the per-endpoint bootstrap.sh that provisioning runs (as root).

    It lays the listener + payload down under /opt/khazad-dum, runs the payload's
    optional provision.sh, and writes the listener config. On AWS it installs the
    listener as a systemd service; on homelab the container's own command launches
    it once the config file appears (so config is written last there).
    """
    common = (
        '#!/usr/bin/env bash\n'
        'set -euo pipefail\n'
        'HERE="$(cd "$(dirname "$0")" && pwd)"\n'
        'DEST=/opt/khazad-dum\n'
        'mkdir -p "$DEST/experiment"\n'
        'cp "$HERE/server.py" "$DEST/server.py"\n'
        'cp -R "$HERE/payload/." "$DEST/experiment/"\n'
        'chmod +x "$DEST/experiment/run" 2>/dev/null || true\n'
        'command -v python3 >/dev/null 2>&1 || { apt-get update -y && apt-get install -y python3; }\n'
        'if [ -f "$DEST/experiment/provision.sh" ]; then bash "$DEST/experiment/provision.sh"; fi\n'
    )
    write_config = (
        f'cat > "$DEST/listener.config.json" <<\'JSON\'\n'
        f'{{"role": "{role}", "port": {port}, "payload_dir": "/opt/khazad-dum/experiment"}}\n'
        f'JSON\n'
    )
    if target == "aws":
        systemd = (
            "cat > /etc/systemd/system/khazad-listener.service <<'UNIT'\n"
            "[Unit]\n"
            "Description=khazad-dum experiment listener\n"
            "After=network.target\n"
            "[Service]\n"
            "Environment=KHAZAD_LISTENER_CONFIG=/opt/khazad-dum/listener.config.json\n"
            "ExecStart=/usr/bin/python3 /opt/khazad-dum/server.py\n"
            "Restart=always\n"
            "[Install]\n"
            "WantedBy=multi-user.target\n"
            "UNIT\n"
            "systemctl daemon-reload\n"
            "systemctl enable --now khazad-listener.service\n"
        )
        return common + write_config + systemd
    # homelab: the container command waits for server.py + config, so write
    # config last (after the payload's provisioning has finished).
    return common + write_config


def cmd_build(args: argparse.Namespace) -> None:
    project_root = _project_root()
    _require_init(project_root)
    experiment = project_root.name

    servers = _load_experiment_servers(project_root)
    _validate_servers(servers, project_root)

    tf.ensure_tf_home()
    tf.generate_ssh_keys(experiment)

    listener_text = _listener_source()
    data = tf.load_servers()
    # Replace this experiment's entries, leaving other experiments untouched.
    data["servers"] = {
        k: v for k, v in data["servers"].items() if v.get("experiment") != experiment
    }
    for s in servers:
        bundle = tf.stage_bundle(
            experiment,
            s["name"],
            (project_root / s["payload_dir"]).resolve(),
            listener_text,
            _bootstrap_text(s["target"], s["role"], tf.LISTENER_PORT),
        )
        entry = {
            "name": s["name"],
            "experiment": experiment,
            "target": s["target"],
            "role": s["role"],
            "bundle_dir": str(bundle),
            "listener_port": tf.LISTENER_PORT,
        }
        if s["target"] == "aws":
            entry["region"] = s["region"]
            entry["instance_type"] = tf.DEFAULT_INSTANCE_TYPE
        else:
            entry["docker_image"] = s["docker_image"]
        data["servers"][f"{experiment}__{s['name']}"] = entry
    tf.save_servers(data)

    print(f"[khazad-dum] Building experiment '{experiment}' ({len(servers)} endpoint(s))...")
    env = tf.tf_env()
    tf.init(env)
    tf.apply(env)

    endpoints = tf.output_endpoints(env)
    mine = {k: v for k, v in endpoints.items() if v.get("experiment") == experiment}
    if not mine:
        print("[khazad-dum] No endpoint outputs found; skipping summary prompt.")
        return

    prompt = _build_summary_prompt(experiment, mine)
    print(f"[khazad-dum] Experiment '{experiment}' deployed. Summarising infrastructure...")
    # The summary is pure prompt-in / text-out — no files to touch — so run it
    # in TEXT mode. Fall back to printing the prompt if claude is unavailable.
    try:
        claude_sdk.run_prompt(prompt, mode=claude_sdk.Mode.TEXT)
    except claude_sdk.ClaudeUnavailable:
        print("[khazad-dum] claude unavailable; printing summary prompt instead:\n")
        print(prompt)


def cmd_destroy(args: argparse.Namespace) -> None:
    project_root = _project_root()
    experiment = project_root.name

    tf.ensure_tf_home()
    data = tf.load_servers()
    before = len(data["servers"])
    data["servers"] = {
        k: v for k, v in data["servers"].items() if v.get("experiment") != experiment
    }
    removed = before - len(data["servers"])
    if removed == 0:
        print(f"[khazad-dum] No servers found for experiment '{experiment}'. Nothing to destroy.")
        return
    tf.save_servers(data)

    print(f"[khazad-dum] Destroying {removed} endpoint(s) for experiment '{experiment}'...")
    env = tf.tf_env()
    tf.init(env)
    tf.apply(env)

    key_dir = tf.KEYS_DIR / experiment
    if key_dir.exists():
        shutil.rmtree(key_dir)
    print(f"[khazad-dum] Experiment '{experiment}' destroyed.")


# ── Experiment control plane: run → fetch → graph → report ────────────────────

def _experiment_endpoints(project_root: Path) -> dict:
    """Endpoints for this experiment, read from terraform outputs (over Twingate)."""
    tf.ensure_tf_home()
    endpoints = tf.output_endpoints(tf.tf_env())
    mine = {k: v for k, v in endpoints.items() if v.get("experiment") == project_root.name}
    if not mine:
        sys.exit(
            "No provisioned endpoints found for this experiment. "
            "Run `khazad-dum build experiment` first."
        )
    return mine


def _listener_url(endpoint: dict, path: str) -> str:
    return f"http://{endpoint['address']}:{endpoint['listener_port']}{path}"


def _http(url: str, *, method: str, data: bytes | None = None, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (trusted, over Twingate)
        return resp.read()


def cmd_start(args: argparse.Namespace) -> None:
    project_root = _project_root()
    _require_init(project_root)
    endpoints = _experiment_endpoints(project_root)

    # The client (e.g. role "local") needs the server's address as its peer; in
    # the two-endpoint model each endpoint's peer is simply the other one.
    addr_by_role: dict[str, str] = {}
    for v in endpoints.values():
        addr_by_role.setdefault(v["role"], v["address"])

    for ep in sorted(endpoints.values(), key=lambda s: s["name"]):
        peer = next((a for r, a in addr_by_role.items() if r != ep["role"]), "")
        body = json.dumps({"peer_addr": peer}).encode()
        try:
            _http(_listener_url(ep, "/run"), method="POST", data=body)
        except urllib.error.HTTPError as exc:
            sys.exit(f"[khazad-dum] {ep['name']}: listener rejected /run ({exc.code} {exc.reason}).")
        except (urllib.error.URLError, OSError) as exc:
            sys.exit(
                f"[khazad-dum] {ep['name']}: cannot reach listener at {ep['address']} "
                f"({exc}). Is the Twingate client up?"
            )
        print(f"[khazad-dum] {ep['name']}: experiment started (peer={peer or '-'}).")

    _poll_until_done(endpoints, timeout=args.timeout)


def _poll_until_done(endpoints: dict, *, timeout: int) -> None:
    # The local app drives the benchmark and records the results, so the run is
    # complete once it finishes — we don't wait on the remote (server) side. A
    # well-behaved server self-terminates; either way `destroy` cleans up, and
    # blocking on a forever-server would just burn the whole timeout.
    pending = {ep["name"]: ep for ep in endpoints.values() if ep.get("role") == "local"}
    pending = pending or {ep["name"]: ep for ep in endpoints.values()}
    deadline = time.time() + timeout
    while pending and time.time() < deadline:
        time.sleep(5)
        for name, ep in list(pending.items()):
            try:
                status = json.loads(_http(_listener_url(ep, "/status"), method="GET"))
            except (urllib.error.URLError, OSError):
                continue
            state = status.get("state")
            if state in ("done", "failed"):
                print(f"[khazad-dum] {name}: {state} (exit {status.get('exit_code')}).")
                pending.pop(name)
    if pending:
        print(f"[khazad-dum] Timed out waiting for: {', '.join(pending)}. Fetch later with `fetch`.")
    else:
        print("[khazad-dum] Client finished. Run `khazad-dum fetch experiment`.")


def cmd_fetch(args: argparse.Namespace) -> None:
    project_root = _project_root()
    _require_init(project_root)
    endpoints = _experiment_endpoints(project_root)

    results_root = _docs_root(project_root) / EXPERIMENT_DIR / "process" / RESULTS_DIR_NAME
    for ep in sorted(endpoints.values(), key=lambda s: s["name"]):
        try:
            blob = _http(_listener_url(ep, "/results"), method="GET", timeout=120)
        except urllib.error.HTTPError as exc:
            print(f"[khazad-dum] {ep['name']}: no results yet ({exc.code} {exc.reason}).")
            continue
        except (urllib.error.URLError, OSError) as exc:
            print(f"[khazad-dum] {ep['name']}: cannot reach listener ({exc}).")
            continue
        dest = results_root / ep["name"]
        _extract_results(blob, dest)
        print(f"[khazad-dum] {ep['name']}: results -> {dest.relative_to(project_root)}")


def _extract_results(tar_bytes: bytes, dest: Path) -> None:
    """Extract a listener results.tar.gz into dest, stripping the leading
    ``results/`` arc component so files land directly under dest."""
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:gz") as tar:
        for member in tar.getmembers():
            parts = member.name.split("/")
            if parts and parts[0] == "results":
                parts = parts[1:]
            if not parts or not parts[0]:
                continue
            member.name = "/".join(parts)
            tar.extract(member, dest)  # noqa: S202 (trusted source over Twingate)


def _build_experiment_analysis_prompt(sub_prompt: str, project_root: Path) -> str:
    prompt = _template_text(f"{EXPERIMENT_DIR}/prompts/{sub_prompt}.md")
    results_dir = _docs_root(project_root) / EXPERIMENT_DIR / "process" / RESULTS_DIR_NAME
    manifest = sorted(
        str(p.relative_to(project_root))
        for p in results_dir.rglob("*")
        if p.is_file()
    )
    parts = [prompt]
    parts.extend(_experiment_input_sections(project_root))
    if manifest:
        listing = "\n".join(f"- {m}" for m in manifest)
        parts.append(f"---\n\n## Fetched result files\n\n{listing}")
    for tname in _SUB_PROMPT_TEMPLATES.get(sub_prompt, ()):
        tmpl = _template_text(f"{EXPERIMENT_DIR}/templates/{tname}.md")
        parts.append(f"---\n\n## Template\n\n{tmpl}")
    return "\n\n".join(parts)


def _run_experiment_analysis(sub_prompt: str, label: str) -> None:
    project_root = _project_root()
    _require_init(project_root)
    results_dir = _docs_root(project_root) / EXPERIMENT_DIR / "process" / RESULTS_DIR_NAME
    if not results_dir.is_dir() or not any(results_dir.rglob("*")):
        sys.exit("No fetched results found. Run `khazad-dum fetch experiment` first.")
    prompt = _build_experiment_analysis_prompt(sub_prompt, project_root)
    tokens = assert_within_limit(prompt)
    print(f"[khazad-dum] {label}: {tokens} tokens (limit {MAX_TOKENS}).")
    result = _invoke(prompt, project_root)
    if result.is_error:
        print(f"[khazad-dum] claude reported an error ({result.subtype or 'unknown'}).")
        sys.exit(1)


def cmd_graph(args: argparse.Namespace) -> None:
    _run_experiment_analysis("analyse-results", "Graphing experiment results")


def cmd_report(args: argparse.Namespace) -> None:
    _run_experiment_analysis("experiment-report", "Writing experiment report")


def _build_summary_prompt(experiment: str, endpoints: dict) -> str:
    prompt = _template_text(f"{EXPERIMENT_DIR}/prompts/summary.md")
    template = _template_text(f"{EXPERIMENT_DIR}/templates/summary.md")

    key_path = tf.KEYS_DIR / experiment / "id_rsa"
    lines: list[str] = []
    for info in sorted(endpoints.values(), key=lambda s: s["name"]):
        lines.append(f"- **{info['name']}** — {info['target']} / role={info['role']}")
        lines.append(
            f"  - Twingate address: {info['address']} (listener port {info['listener_port']})"
        )
        if info.get("public_ip"):  # AWS endpoints only
            lines.append(f"  - ssh: `ssh -i {key_path} ubuntu@{info['public_ip']}`")
    rendered = template.replace("{{EXPERIMENT}}", experiment).replace(
        "{{SERVERS}}", "\n".join(lines)
    )
    return f"{prompt}\n{rendered}"


def cmd_tokens(args: argparse.Namespace) -> None:
    text = Path(args.file).read_text() if args.file else sys.stdin.read()
    print(count_tokens(text))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="khazad-dum", description="Walk a project through Research → Delivery using claude.")
    sub = p.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="Create documentation/ scaffold in the current directory.")
    p_init.add_argument("--force", action="store_true", help="Proceed even if documentation/ exists.")
    p_init.set_defaults(func=cmd_init)

    p_status = sub.add_parser("status", help="Show step progress.")
    p_status.set_defaults(func=cmd_status)

    p_run = sub.add_parser("run", help="Invoke claude on a step (default: next pending).")
    p_run.add_argument("step", nargs="?", help="Step slug or number (e.g. research, 1).")
    p_run.add_argument("--dry-run", action="store_true", help="Print prompt without invoking claude.")
    p_run.set_defaults(func=cmd_run)

    p_build = sub.add_parser("build", help="Provision infrastructure for a phase.")
    p_build.add_argument("target", choices=["experiment"], help="What to build.")
    p_build.set_defaults(func=cmd_build)

    p_destroy = sub.add_parser("destroy", help="Tear down infrastructure for a phase.")
    p_destroy.add_argument("target", choices=["experiment"], help="What to destroy.")
    p_destroy.set_defaults(func=cmd_destroy)

    # Experiment control plane: build → start → fetch → graph → report.
    p_start = sub.add_parser("start", help="Trigger the experiment run on each endpoint (over Twingate).")
    p_start.add_argument("target", choices=["experiment"], help="What to start.")
    p_start.add_argument("--timeout", type=int, default=1800, help="Seconds to wait for runs to finish (default 1800).")
    p_start.set_defaults(func=cmd_start)

    p_fetch = sub.add_parser("fetch", help="Fetch results from each endpoint into process/results/.")
    p_fetch.add_argument("target", choices=["experiment"], help="What to fetch.")
    p_fetch.set_defaults(func=cmd_fetch)

    p_graph = sub.add_parser("graph", help="Graph fetched results (python stats/plots) into output/graphs/.")
    p_graph.add_argument("target", choices=["experiment"], help="What to graph.")
    p_graph.set_defaults(func=cmd_graph)

    p_report = sub.add_parser("report", help="Write the experiment report into output/.")
    p_report.add_argument("target", choices=["experiment"], help="What to report on.")
    p_report.set_defaults(func=cmd_report)

    p_tokens = sub.add_parser("tokens", help="Count tokens in a file or stdin.")
    p_tokens.add_argument("file", nargs="?", help="Path to a file. If omitted, reads stdin.")
    p_tokens.set_defaults(func=cmd_tokens)

    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        cmd_status(args)
        return
    args.func(args)


if __name__ == "__main__":
    main()
