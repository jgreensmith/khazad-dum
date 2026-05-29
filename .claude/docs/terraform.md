# Terraform / Experiment Infrastructure

Powers the experiment pipeline `build → start → fetch → graph → report`. Code: `terraform.py` +
`cli.py`. Packaged `.tf` skeleton: `src/khazad_dum/terraform/` (root + `modules/experiment_server/`).

## Topology (fixed, WAN-comms benchmarking)
One experiment = **two endpoints** reachable over a **Twingate TLS tunnel**:
- **remote app** — AWS EC2 Ubuntu host (`target:"aws"`, `role:"remote"`), the server side.
- **local app** — Docker container on computron (`target:"homelab"`, `role:"local"`), the client/driver.

Both the data plane (the apps benchmarking each other) and the control plane (khazad-dum on the
laptop triggering/collecting) traverse Twingate. The laptop is already a Twingate client; the
**homelab connector already runs on computron**, so terraform only adds a `twingate_resource` for the
container inside the existing remote network named by `var.tg_homelab_remote_network`
(looked up with `data.twingate_remote_network`). AWS endpoints get a per-experiment remote network +
connector (EC2) as before.

## Listener (fixed infra) vs payload (project-specific)
Provisioning always installs a generic stdlib Python **listener** (`src/khazad_dum/listener/`, shipped
into each bundle as `server.py`) — systemd unit on AWS, the container's foreground command on homelab.
It exposes `GET /health`, `POST /run` (non-blocking; optional `{"peer_addr"}` body), `GET /status`,
`GET /results` (tar.gz). It runs the project **payload** (executable `run` + optional `provision.sh`),
authored by the Experiment gate workflow, conforming to `$KHAZAD_ROLE`/`$KHAZAD_PEER_ADDR`/
`$KHAZAD_RESULTS_DIR`/`$KHAZAD_RUN_ID`.

## Per-endpoint bundle
`cli.cmd_build` stages, per endpoint, a bundle under `~/.khazad-dum/terraform/bundles/<exp>__<name>/`:
`server.py` (listener) + `payload/` (from `input/payload/<name>/`) + a generated `bootstrap.sh`
(target-aware: installs files, runs the payload's provision, writes the listener config; on AWS also
installs+starts the systemd unit). Terraform delivers the whole directory (SSH file provisioner for
AWS; `docker cp` for homelab) and runs `bootstrap.sh`.

## TF home (global, writable)
`~/.khazad-dum/terraform/` (`TF_HOME`). `ensure_tf_home()` copies the packaged `.tf` skeleton on every
command, refreshing `.tf` but never touching `servers.auto.tfvars.json` (CLI-managed desired state),
`keys/<experiment>/` (SSH keypairs), `bundles/`, or terraform state.

## Desired-state model
One global `servers.auto.tfvars.json` holds all experiments in a `servers` map keyed
`<experiment>__<name>`, each `{name, experiment, target, role, bundle_dir, listener_port,
region|instance_type (aws) | docker_image (homelab)}`. `experiment` = project dir name. `build`
replaces only this experiment's entries; `destroy` removes them + the key dir.

## Per-project input
`documentation/02_experiment/input/servers.json` — array of
`{name, target, role, payload_dir, region (aws) | docker_image (homelab)}`, seeded by `init` with a
2-endpoint sample + sample payloads. `_validate_servers` enforces target ∈ {aws,homelab}, region ∈
`SUPPORTED_REGIONS` (aws), `docker_image` present (homelab), `payload_dir` exists with an executable
`run`, unique names. The AWS provider region is fixed (`eu-west-2`); `region` is informational for now.

## Outputs the control plane uses
`output "endpoints"` (root) merges AWS + homelab endpoints, each `{name, experiment, target, role,
address, listener_port}`. `address` is the Twingate-reachable host (AWS private IP / container docker
IP). `cli.cmd_start`/`cmd_fetch` read it (`tf.output_endpoints`) and call the listeners with
stdlib `urllib`; `start` injects each endpoint's peer address from this output at run time.

## Credentials & secrets — see [[infra-conventions]] memory
- AWS creds via **1Password CLI** (`op read`), injected into the env for provider + MinIO backend.
- Twingate via `TF_VAR_tg_api_token` / `TF_VAR_tg_network` / `TF_VAR_tg_homelab_remote_network`, set by
  `tf_env()` from 1Password (`op://Private/Twingate/...`) unless already present in the environment.
- State backend = **MinIO** on computron (configured in the `.tf` skeleton).

External deps assumed on PATH: `terraform` (>=1.6), `ssh-keygen`, `op`, plus `docker` reachable at
`ssh://james@computron.local`.

## Known live-tweak risk
The homelab Twingate addressing (container docker IP in the existing remote network) and the
app-to-app client routing (the home side reaching the AWS resource) depend on the live tenant setup
and may need a hands-on adjustment on first real run.
