## Workflow 1.2.2 — Draft Experiment (Config & Payload)

The pre-experiment gate has passed. Turn the two plans (consolidated with the questionnaire answers) into
a **draft experiment**, all under `process/`: the two-endpoint server config and the **payload** code each
endpoint runs. Each cycle, create-or-refine the artifacts and append a round of review questions, until
the human is happy to build. You author only the payload — khazad-dum installs the listener and reads the
config + payload straight from `process/` when the human runs `khazad-dum build experiment`. **Never write
to `input/`.**

## Inputs (read-only)
- **Project Description** + **Experiment Plan** (pristine `input/` docs, below).
- `process/pre-experiment-questionnaire.md` — the gate's answers; **fold them into the refined plans**.
- `process/draft-review-questionnaire.md` if it exists — the human's feedback on a previous draft;
  **apply it**.
- The artifacts below if they already exist — **refine in place, don't restart**.
- After a pipeline run: `process/results/<endpoint>/run.log` (+ partial results). If a previous draft
  failed at build/start/fetch, **read these and fix the payload**.

## Each cycle — write to `documentation/02_experiment/process/`
1. **Refined plans** — consolidate the answers into `process/project-description.md` (iteration 2) and
   `process/experiment-plan.md`. These are the spec the rest of this step works from.
2. **`servers.json`** — a JSON array of exactly two endpoints (one remote, one local):
   ```json
   [
     {"name":"remote-app","target":"aws","role":"remote","region":"eu-west-2",
      "payload_dir":"documentation/02_experiment/process/payload/remote-app"},
     {"name":"local-app","target":"homelab","role":"local","docker_image":"python:3.12-slim",
      "payload_dir":"documentation/02_experiment/process/payload/local-app"}
   ]
   ```
   - `region` (aws only): us-east-1/2, us-west-2, eu-west-1/2, eu-central-1 — realistic WAN distance.
   - `docker_image` (homelab only): a base image with `python3` + `bash` (e.g. `python:3.12-slim`).
   - `payload_dir`: points at the payload under `process/` (next item).
3. **Payloads** → `process/payload/<name>/` (one dir per endpoint):
   - An executable **`run`** implementing that endpoint's side. The listener sets these for it:
     `KHAZAD_ROLE` (`local`|`remote`), `KHAZAD_PEER_ADDR` (peer's Twingate host), `KHAZAD_RESULTS_DIR`
     (write results here), `KHAZAD_RUN_ID`.
   - Optional **`provision.sh`** — installs deps / builds at provision time (runs once, as root,
     idempotent). **Do not install or start the listener.**
   - A **`<name>.md`** (use the **script-doc Template**) documenting what the script does — its behaviour,
     the app port, how the server terminates, and every result file it writes. This is what the human
     reviews, so keep it faithful to the script.

## Payload contract (get these right or the run fails)
- **The server (remote) MUST self-terminate** — bound it by time, or stop on an end-of-run signal from
  the client. A server that runs forever never reports `done` and its results can't be fetched while it
  runs.
- **The client MUST tolerate a cold server** — retry the connection for a few seconds before giving up;
  both `run`s start at the same moment.
- **Same app port** on both sides; pick one that isn't the listener's. The client reaches the server at
  `$KHAZAD_PEER_ADDR:<that port>`.
- **Write machine-readable results** (CSV/JSON — per-sample latency, throughput, timestamps) into
  `$KHAZAD_RESULTS_DIR`. A run that records nothing parseable is useless to the graphing step.

## Then — append a draft-review round
Using the **questionnaire Template**, append a `## Round {N}` block (labelled **Draft Review**) to
`process/draft-review-questionnaire.md` (never edit prior rounds): start with a one-line note on what you
drafted/changed and your confidence the scripts are correct, then 3–8 questions inviting the human to
confirm or correct the **script behaviour, app protocol/port, and result schema** (e.g. is the load right?
the metrics complete? the result columns what they expect?). This is the human's channel to fix the
scripts without editing them.

Stop after writing. The human reviews `process/` and answers in-file. They re-run this step to refine, or
— when happy — run `khazad-dum build experiment` (which reads the config + payload from `process/`).
