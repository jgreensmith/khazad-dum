## Workflow 1.2.1 — Experiment Gate (Config or Clarify)

You are a fresh agent entering the **Experiment** step. This is a **looping gate**: each cycle you
either (a) decide the experiment plan is solid enough and produce a **draft experiment
configuration** (server definitions + provision scripts), or (b) decide it is not yet, and produce
a **new questionnaire** of hard clarifying questions for the human to answer. The human refines the
plan between cycles; you never see the previous cycle's reasoning — only the current `input/` and
any questionnaires already in `process/`.

## Inputs (read-only)
- The provided **Project Description** — the human's current experiment plan (iteration 2, carried
  over from the Research phase: the refined project plan + experiment recommendations).
- Any existing questionnaires in `$CWD/documentation/02_experiment/process/` matching
  `pre-experiment-questionnaire-*.md` — read them to see what has already been asked and answered,
  and to determine the current cycle number.

## Step 1 — Determine the cycle
Count the questionnaire files already in `process/` matching `pre-experiment-questionnaire-*.md`.
The current cycle `N` is that count **+ 1**. (If the harness has told you the cycle number, use that
instead.)

## Step 2 — Critically analyse the plan (do this hard)
Your job is to **actively find problems**, not to confirm you understand. The goal of this phase is
to turn the plan into something that can actually run on the available infrastructure. Interrogate
the plan and hunt for everything you would need in order to define:
- **Script requirements** — what exactly must run on each experiment server? Inputs, dependencies,
  expected outputs, how a result is measured, how long it runs, how it reports success/failure.
- **Server infrastructure requirements** — how many servers, which region(s), what must be installed
  at provision time, whether the workload fits the available resources.
- **Ambiguities, gaps, unstated assumptions, contradictions, and feasibility risks** in the above.
Be sceptical and specific. A plan that "seems fine" usually has not been pushed hard enough.

## Available experiment resources (hard constraint)
The only resources available for the experiment are:
- **AWS EC2 instances** provisioned by khazad-dum. Default instance type `t3.micro`. Supported
  regions: `us-east-1`, `us-east-2`, `us-west-2`, `eu-west-1`, `eu-west-2`, `eu-central-1`.
- **A home lab server.**
Every recommendation and config must be achievable with these. Do not assume managed services, GPUs,
or infrastructure outside this set unless you explicitly flag it as out-of-scope.

## Step 3 — Self-assess certainty
Give yourself an honest **percentage certainty (0–100%)** that you fully understand the experiment
well enough to write server definitions and provision scripts that would actually run and produce a
meaningful result without guessing.

## Step 4 — Branch on certainty

### IF certainty < 98%  →  produce a new questionnaire (do NOT write any config)
- Write a **new** file (do not append to or edit any existing questionnaire):
  `$CWD/documentation/02_experiment/process/pre-experiment-questionnaire-{N}.md`
- Use the provided **questionnaire template**.
- At the very top, record the **cycle number** and your **% certainty** from Step 3.
- Turn the problems found in Step 2 into 2–8 clarifying questions targeting the **script
  requirements** and **server infrastructure requirements**. Prefer challenging questions that force
  the human to give **written** answers; other question types are allowed where they fit the template.
- Stop here. The human will refine the plan and re-run this gate.

### IF certainty ≥ 98%  →  produce the draft experiment configuration
Write everything to `process/` only — this is a **draft for human review**. The human reviews it and
promotes the approved files into `input/`; only then does `khazad-dum build` consume them. **Never
write to `input/`.**

1. **Server definitions** → `$CWD/documentation/02_experiment/process/servers.json`
   A JSON **array**, one object per server, each with exactly these fields:
   ```json
   [
     {
       "name": "experiment-01",
       "region": "us-east-1",
       "provision_file": "documentation/02_experiment/input/scripts/experiment-01.sh"
     }
   ]
   ```
   - `name` — unique within the experiment.
   - `region` — one of the supported regions above.
   - `provision_file` — path (relative to project root) to the provision script as it will live
     **after promotion to `input/`** (i.e. under `input/scripts/`), so the paths are correct once the
     human promotes. The script drafts themselves go in `process/scripts/` (next item).
2. **Provision scripts** → `$CWD/documentation/02_experiment/process/scripts/<name>.sh`
   One bash script per server (`#!/usr/bin/env bash`, `set -euo pipefail`). The script runs at
   provision time on a fresh Ubuntu host (login user `ubuntu`); it installs dependencies, lays down
   the experiment workload, and runs/serves it so a result can be collected.
3. **Promotion note** → `$CWD/documentation/02_experiment/process/PROMOTION.md`
   A short checklist telling the human exactly what to copy into `input/` (`servers.json` →
   `input/servers.json`; `scripts/*` → `input/scripts/`) and what to verify before running
   `khazad-dum build experiment`.
