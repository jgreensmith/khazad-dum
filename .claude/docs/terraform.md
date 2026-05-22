# Terraform / Experiment Infrastructure

Powers `khazad-dum build experiment` and `destroy experiment`. Code: `terraform.py`.
Packaged `.tf` skeleton: `src/khazad_dum/terraform/` (root + `modules/experiment_server/`).

## TF home (global, writable)
`~/.khazad-dum/terraform/` (`TF_HOME`). `ensure_tf_home()` copies the packaged `.tf` skeleton
in on every build/destroy, **refreshing `.tf` files but never touching**:
- `servers.auto.tfvars.json` (`SERVERS_TFVARS`) — the CLI-managed desired state.
- `keys/<experiment>/` (`KEYS_DIR`) — per-experiment SSH keypairs.
- terraform state.

## Desired-state model
One global `servers.auto.tfvars.json` holds **all** experiments' servers in a `servers` map,
keyed `"<experiment>__<server-name>"`, each `{name, region, experiment, provision_file,
instance_type}`. `experiment` = the project directory name (`project_root.name`).
`build` replaces only this experiment's entries (leaves others); `destroy` removes only this
experiment's entries, then deletes its key dir. So one TF workspace multiplexes many projects.

## Per-project input
`documentation/02_experiment/input/servers.json` — array of `{name, region, provision_file}`,
seeded by `init` (`SERVERS_JSON_TEMPLATE` in cli.py) alongside a sample `provision.sh`.
`_validate_servers` enforces: non-empty, unique names, `region ∈ SUPPORTED_REGIONS`,
`provision_file` exists. Default instance type `t3.micro`.

`SUPPORTED_REGIONS` (terraform.py) must mirror the provider/module blocks in
`terraform/main.tf`: us-east-1/2, us-west-2, eu-west-1/2, eu-central-1.

## Credentials & secrets — see [[infra-conventions]] memory
- AWS creds are read at apply-time from **1Password CLI** (`op read`), refs
  `op://Private/AWS_CLI/access_key_id` and `.../secret_access_key`, injected into the env for
  the provider and backend (`aws_env()`). Requires `op` on PATH and an unlocked vault.
- Terraform **state backend is MinIO** on the home server (`computron.local`) — configured in
  the `.tf` skeleton, not in Python.

## Flow
`build`: validate → `ensure_tf_home` → `generate_ssh_keys` (rsa 4096, skip if present) →
update tfvars → `terraform init` + `apply -auto-approve` → read `output "servers"` → build a
summary prompt (`_build_summary_prompt`, uses `02_experiment/prompts/summary.md` +
`templates/summary.md`) and feed it to `claude -p`.
`destroy`: drop this experiment from tfvars → `init` + `apply` → `rmtree` its key dir.

External deps assumed on PATH: `terraform` (>=1.6), `ssh-keygen`, `op`. Each is checked with a
clear `sys.exit` message if missing.
