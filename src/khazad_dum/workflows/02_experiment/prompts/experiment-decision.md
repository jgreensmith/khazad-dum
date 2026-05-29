## Workflow 1.2.1 — Experiment Gate (Config or Clarify)

You are a fresh agent entering the **Experiment** step. This is a **looping gate**: each cycle you
either (a) decide the experiment plan is solid enough and produce a **draft experiment
configuration** (the two-endpoint server config + the experiment **payload** code), or (b) decide it
is not yet, and produce a **new questionnaire** of hard clarifying questions for the human to answer.
The human refines the plan between cycles; you never see the previous cycle's reasoning — only the
current `input/` and any questionnaires already in `process/`.

## The experiment model (fixed scope — hard constraint)
For now, **every experiment benchmarks communication over the WAN** — measuring protocol behaviour
across a real wide-area link (higher, more variable latency than a LAN can show). The topology is
**fixed** and you must design within it:

- A **remote app** on an **AWS EC2 Ubuntu** host (`target: "aws"`, `role: "remote"`).
- A **local app** in a **Docker container on the home lab** (computron) (`target: "homelab"`,
  `role: "local"`).
- The two apps reach each other over a **Twingate TLS tunnel** — this is the WAN link under test.
  By convention the **remote** endpoint is the **server** side (it serves the protocol under test);
  the **local** endpoint is the **client/driver** (it generates load and records the measurements).

**What protocol(s) and metric(s)** to benchmark is **not** fixed — derive that from the Project
Description (the iteration-2 plan carried over from Research). Your job is to turn the plan into a
configuration and payload that will actually run on this topology and produce a meaningful result.

## How khazad-dum runs an experiment (so you author the payload correctly)
khazad-dum installs a **fixed listener** on each endpoint automatically — **you do not write,
install, or manage the listener.** You only author the **payload** it runs. The flow is
`build → start → fetch → graph → report`:
- On `start`, the listener executes your payload's **`run`** entrypoint on each endpoint. `run` must
  run the experiment **to completion** and write all outputs into the directory given by the
  environment variable **`$KHAZAD_RESULTS_DIR`**.
- These environment variables are provided to `run`:
  - `KHAZAD_ROLE` — `local` or `remote`.
  - `KHAZAD_PEER_ADDR` — the **peer endpoint's Twingate address** (host only). The client connects to
    it on whatever **app port** your payload chose for the server side.
  - `KHAZAD_RESULTS_DIR` — absolute path; write results here.
  - `KHAZAD_RUN_ID` — the current run id.
- On `fetch`, khazad-dum pulls everything under `$KHAZAD_RESULTS_DIR` back to the laptop. **Write
  results as machine-readable data** (CSV or JSON — e.g. per-sample latency, throughput, timestamps)
  so the graphing step can plot them. A run that records nothing parseable is useless.

## Inputs (read-only)
- The provided **Project Description** — the human's current experiment plan (iteration 2: the
  refined project plan + experiment recommendations from Research).
- Any existing questionnaires in `$CWD/documentation/02_experiment/process/` matching
  `pre-experiment-questionnaire-*.md` — read them to see what has already been asked, and to
  determine the current cycle number.

## Step 1 — Determine the cycle
Count the questionnaire files already in `process/` matching `pre-experiment-questionnaire-*.md`.
The current cycle `N` is that count **+ 1**. (If the harness has told you the cycle number, use that.)

## Step 2 — Critically analyse the plan (do this hard)
Your job is to **actively find problems**, not to confirm you understand. Interrogate the plan and
hunt for everything you need in order to design a working experiment on the fixed topology above:
- **Protocol & metrics** — exactly which protocol(s)/transport(s) are under test, and which metrics
  decide the question (latency distribution, throughput, jitter, connection setup time, loss…)?
- **Server side (remote app)** — what must it serve, on what app port, with what dependencies?
- **Client side (local app)** — what load pattern, how many samples / how long, what does it record?
- **Result format** — what files, columns/fields, units — enough for the graphing step to plot.
- **Ambiguities, gaps, unstated assumptions, contradictions, and feasibility risks** in the above.
Be sceptical and specific. A plan that "seems fine" usually has not been pushed hard enough.

## Step 3 — Self-assess certainty
Give yourself an honest **percentage certainty (0–100%)** that you understand the experiment well
enough to write the two payloads and the server config such that they would actually run on this
topology and produce a meaningful result without guessing.

## Step 4 — Branch on certainty

### IF certainty < 98%  →  produce a new questionnaire (do NOT write any config or payload)
- Write a **new** file (do not append to or edit any existing questionnaire):
  `$CWD/documentation/02_experiment/process/pre-experiment-questionnaire-{N}.md`
- Use the provided **questionnaire template**. At the top, record the **cycle number** and your
  **% certainty** from Step 3.
- Turn the problems found in Step 2 into 2–8 clarifying questions targeting the protocol/metrics, the
  server and client behaviour, and the result format. Prefer challenging questions that force the
  human to give **written** answers.
- Stop here. The human will refine the plan and re-run this gate.

### IF certainty ≥ 98%  →  produce the draft experiment configuration + payload
Write everything to `process/` only — this is a **draft for human review**. The human reviews it and
promotes the approved files into `input/`; only then does `khazad-dum build` consume them. **Never
write to `input/`.**

1. **Server config** → `$CWD/documentation/02_experiment/process/servers.json`
   A JSON **array** of exactly two endpoints (one remote, one local), each with these fields:
   ```json
   [
     {
       "name": "remote-app",
       "target": "aws",
       "role": "remote",
       "region": "eu-west-2",
       "payload_dir": "documentation/02_experiment/input/payload/remote-app"
     },
     {
       "name": "local-app",
       "target": "homelab",
       "role": "local",
       "docker_image": "python:3.12-slim",
       "payload_dir": "documentation/02_experiment/input/payload/local-app"
     }
   ]
   ```
   - `region` (aws only) — one of: us-east-1, us-east-2, us-west-2, eu-west-1, eu-west-2, eu-central-1.
     Pick a region that gives a realistic WAN distance for the question being asked.
   - `docker_image` (homelab only) — a base image that already provides `python3` and `bash`
     (e.g. `python:3.12-slim`), so the listener can run.
   - `payload_dir` — the path **after promotion to `input/`** (the drafts go in `process/payload/...`,
     next item).

2. **Payloads** → `$CWD/documentation/02_experiment/process/payload/<name>/` (one dir per endpoint)
   - An executable **`run`** (`#!/usr/bin/env bash` or any interpreter present on the image/host)
     implementing that endpoint's side of the benchmark per the contract above (server vs client by
     `$KHAZAD_ROLE`, peer at `$KHAZAD_PEER_ADDR`, results into `$KHAZAD_RESULTS_DIR`).
   - An optional **`provision.sh`** that installs dependencies / builds the app at provision time
     (runs once, as root). Keep it idempotent. **Do not install or start the listener** — that is
     handled for you.
   - Keep the two payload dirs consistent: the client must connect to the **same app port** the
     server listens on.

3. **Promotion note** → `$CWD/documentation/02_experiment/process/PROMOTION.md`
   A short checklist telling the human exactly what to copy into `input/` (`servers.json` →
   `input/servers.json`; `payload/<name>/*` → `input/payload/<name>/`; keep `run` executable) and the
   run order afterwards: `khazad-dum build experiment` → `start` → `fetch` → `graph` → `report`.
