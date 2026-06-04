# Step 02 — Experiment (Claude)

Second Phase-1 step. Designs and runs a **WAN-communication benchmark** on a fixed two-endpoint
topology, then folds the result into the plan. Iteration 2 → experiment output (iter 3).
Infra detail: see [terraform.md](../terraform.md).

## Pattern
Gate + complete (certainty loop) **plus** a fixed infra pipeline `build → start → fetch → graph → report`.

## Fixed topology (hard constraint)
Every experiment benchmarks comms over the WAN: a **remote app** on AWS EC2 (`target:"aws"`,
`role:"remote"`, server side) ⇄ a **local app** in a Docker container on computron
(`target:"homelab"`, `role:"local"`, client/driver), talking over a **Twingate TLS tunnel** (data
plane *and* khazad-dum's control plane). Protocol/metrics are derived from the plan, not fixed.

## Sub-prompts (workflow)
- **1.2.1 `experiment-decision`** (gate, loops): analyse the iter-2 plan → % certainty. **<98%** →
  `process/pre-experiment-questionnaire-{N}.md`, stop. **≥98%** → draft to `process/`:
  `servers.json` (2 endpoints), the **payload** (`payload/<name>/run` + optional `provision.sh`), and
  `PROMOTION.md`. **Human promotes the drafts into `input/`** — only then does `build` consume them.
- **1.2.2 `complete-experiment-step`**: after build/start/fetch/graph/report + human refinement →
  `output/finalised-project-plan.md` (iter 3).

## Listener vs payload
The **listener** is fixed infra (`src/khazad_dum/listener/`, installed on every endpoint) — the gate
never touches it. The gate authors only the **payload** it runs: an executable `run` honouring
`$KHAZAD_ROLE` / `$KHAZAD_PEER_ADDR` / `$KHAZAD_RESULTS_DIR` / `$KHAZAD_RUN_ID`, writing
machine-readable (CSV/JSON) results.

## Helper prompts (not in the workflow tree)
- **`analyse-results`** (the `graph` stage): pandas/matplotlib over fetched results → PNGs +
  `output/graphs/stats.json`.
- **`experiment-report`** (the `report` stage): interprets graphs+stats vs the plan →
  `output/experiment-report.md`.
- `summary.md` = build-time infra briefing.

## In → out
- **In:** `input/` plan (iter 2) → human-promoted `input/servers.json` + `input/payload/`.
- **Out:** `output/{experiment-report.md,graphs/,finalised-project-plan.md}`; raw results in
  `process/results/`; drafts + questionnaires in `process/`.

## Flow
gate → (drafts to `process/`) → human promotes to `input/` → `build`→`start`→`fetch`→`graph`→`report`
→ human refines `input/` → complete → finalised-project-plan (iter 3).

## Key files
`workflows/02_experiment/prompts/{experiment-decision,complete-experiment-step,analyse-results,experiment-report,summary}.md`;
templates `templates/{questionnaire,experiment-report,project-description,summary}.md`.
CLI: `cli.cmd_build/start/fetch/graph/report`; infra: `terraform.py`, `terraform/`, `listener/`.
