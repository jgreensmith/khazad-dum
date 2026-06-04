# Step 02 — Experiment (Claude)

Second Phase-1 step. Designs and runs a **WAN-communication benchmark** on a fixed two-endpoint
topology, then folds the result into the plan. Mirrors step 01's `gate → draft/refine → complete` shape,
wrapped around the fixed infra pipeline. Infra detail: see [terraform.md](../terraform.md).

## Pattern
Pristine-input, human-advanced, looping — like step 01. Two human-owned input docs stay unchanged; the
human answers questionnaires in-file and the agent folds the answers into `process/` iterations. Four
sub-prompts wrap the fixed `build → start → fetch → graph → report` pipeline.

## Fixed topology (hard constraint)
Every experiment benchmarks comms over the WAN: a **remote app** on AWS EC2 (`target:"aws"`,
`role:"remote"`, server side) ⇄ a **local app** in a Docker container on computron (`target:"homelab"`,
`role:"local"`, client/driver), over a **Twingate TLS tunnel** (data plane *and* khazad-dum's control
plane). Protocol/metrics derive from the plan, not fixed.

## Inputs (pristine, two docs)
`input/` holds **only** `project-description.md` (project context, promoted iteration-1 from Research) and
`input/experiment-plan.md` (the experiment design). Both stay unchanged through the step; the human answers
questionnaires in-file. The agent injects **both** into every step-02 prompt and writes everything else
(refined plans, `servers.json`, `payload/`, results) to `process/` — never `input/`. There is **no
promotion**: `build` reads the config + payload from `process/`.

## Sub-prompts (workflow)
- **1.2.1 `experiment-gate`** (pre-gate, loops): challenge *both* input docs → append `## Round {N}`
  (certainty % + recommendation) to `process/pre-experiment-questionnaire.md`. Questions only; human
  advances.
- **1.2.2 `draft-experiment`** (loops): fold answers → `process/project-description.md` (iter 2) +
  `process/experiment-plan.md`; draft `process/servers.json` + `process/payload/<name>/{run,provision.sh,
  <name>.md}`; append a **Draft Review** round to `process/draft-review-questionnaire.md` (the human's
  channel to correct the scripts without editing them). Carries the payload contract. On re-run, reads the
  review answers + `process/results/**/run.log` to refine/fix the payload. Human runs the pipeline when
  happy — `build` reads config + payload straight from `process/` (no promotion).
- **1.2.3 `interpret-and-refine`** (post-gate, loops): create/refine `process/finalised-project-plan.md`
  (iter 3) + append `## Round {N}` to `process/post-experiment-questionnaire.md` challenging what the
  report means. Human advances.
- **1.2.4 `complete-experiment-step`**: QC + promote the finalised plan `process/ → output/`.

## Listener vs payload
The **listener** is fixed infra (`src/khazad_dum/listener/`, installed on every endpoint) — the gate
never touches it. `draft-experiment` authors only the **payload**: an executable `run` honouring
`$KHAZAD_ROLE`/`$KHAZAD_PEER_ADDR`/`$KHAZAD_RESULTS_DIR`/`$KHAZAD_RUN_ID`, writing machine-readable
(CSV/JSON) results. **Payload contract:** the server (remote) must self-terminate (time-box or client
end-signal); the client (local) must retry a cold server; both sides share one app port.

## Helper prompts (not in the workflow tree)
- **`analyse-results`** (the `graph` stage): pandas/matplotlib over fetched results → PNGs +
  `output/graphs/stats.json`.
- **`experiment-report`** (the `report` stage): interprets graphs+stats vs the plan →
  `output/experiment-report.md`, **with a mermaid topology diagram and the payload script-docs as
  appendices**.
- `summary.md` = build-time infra briefing.

## Pipeline (fixed)
`build` (terraform: 2 endpoints + listener + Twingate) → `start` (trigger each payload `run`; poll the
**local/client** side to completion — the server is not waited on) → `fetch` (results →
`process/results/`) → `graph` → `report`. `destroy` tears it down.

## In → out
- **In:** pristine `input/{project-description,experiment-plan}.md` (the only files in `input/`). The
  agent's `process/servers.json` + `process/payload/` are read directly by `build` — no promotion.
- **Out:** `output/{experiment-report.md,graphs/,finalised-project-plan.md}`; raw results in
  `process/results/`; refined plans, drafts, script-docs + three questionnaires in `process/`.

## Flow
gate (loops) → draft-experiment (drafts to `process/` + draft-review questionnaire, loops) →
`build→start→fetch→graph→report` (build reads `process/`) → interpret-and-refine (iter-3 in `process/`,
loops) → complete (promote to `output/`). On a broken payload, re-run `draft-experiment` (reads `run.log`
+ the review answers).

## Key files
`workflows/02_experiment/prompts/{experiment-gate,draft-experiment,interpret-and-refine,
complete-experiment-step,analyse-results,experiment-report,summary}.md`; templates
`templates/{questionnaire,project-description,experiment-plan,script-doc,experiment-report,summary}.md`.
CLI: `cli.cmd_build/start/fetch/graph/report`; infra: `terraform.py`, `terraform/`, `listener/`.
