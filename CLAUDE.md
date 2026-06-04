# khazad-dum — Agent Index

Python CLI that drives a project through **6 steps (across 2 phases)** using Claude. Each `run`
assembles a prompt from packaged workflow markdown + the project's `scope.md`, token-checks
it (tiktoken `cl100k_base`, 180k limit), then runs it through the **Agent SDK**
(`claude_sdk.run_prompt`, mode-scoped tool access; uses the local `claude` binary under
subscription auth). The experiment phase has a `build`→`start`→`fetch`→`graph`→`report` pipeline that
provisions a two-endpoint WAN-comms experiment (AWS EC2 + a homelab Docker container, reachable over a
Twingate TLS tunnel) via Terraform + a packaged listener, then runs/collects/visualises it.

**This file is an index. Read the linked doc only when working in that area — do not load all of them.**

## Docs (read on demand)
- [.claude/docs/architecture.md](.claude/docs/architecture.md) — module map, prompt-assembly data flow, state model.
- [.claude/docs/workflows.md](.claude/docs/workflows.md) — the 6-step model, the gate/loop/complete patterns, iteration model, **authoring conventions for prompts/templates**; links to the per-step docs.
- [.claude/docs/terraform.md](.claude/docs/terraform.md) — `build`/`destroy`, TF home, 1Password creds, MinIO state backend, regions.
- [.claude/docs/roadmap.md](.claude/docs/roadmap.md) — **project state: active work, the full Deferred CLI work list, known gaps.** Read this for "what's left to do".

### Per-step design ([.claude/docs/steps/](.claude/docs/steps/))
- [01_research.md](.claude/docs/steps/01_research.md) — gate+complete certainty loop → literature review + refined plan + experiment recs.
- [02_experiment.md](.claude/docs/steps/02_experiment.md) — gate → draft → interpret → complete around the `build→start→fetch→graph→report` WAN benchmark; pristine two-doc inputs; listener vs payload.
- [03_architecture.md](.claude/docs/steps/03_architecture.md) — domain-modelling loop+complete; C4/DDD; scaffolds the cargo skeleton; writes `test_commands`.
- [04_project_management.md](.claude/docs/steps/04_project_management.md) — vertical-slicing loop+complete; emits per-feature `scope.md` + `branch-plan.json`.
- [05_developer_orchestration.md](.claude/docs/steps/05_developer_orchestration.md) — Phase 2: the 9-phase deterministic TDD state machine.
- [06_delivery_and_maintenance.md](.claude/docs/steps/06_delivery_and_maintenance.md) — Phase 2 step 2.2; **not yet authored** (deliverables undefined).

> Human-facing guides (2–5 pp each, with mermaid control-flow diagrams) live in
> [`documentation/steps/`](documentation/steps/) — for the reader, not the agent.

## Source map
- `src/khazad_dum/cli.py` — argparse entry (`main`); commands: `init`, `status` (default), `run`, `build`, `start`, `fetch`, `graph`, `report`, `destroy`, `tokens`. `_invoke` drives a step prompt through the SDK in WRITE mode; `start`/`fetch` call the endpoint listeners over Twingate (stdlib `urllib`); `graph`/`report` invoke WRITE-mode analysis prompts; `cmd_build` stages per-endpoint bundles + emits `target`/`role`/`docker_image`.
- `src/khazad_dum/listener/` — **fixed-infra** stdlib HTTP listener (`server.py`, also runnable standalone) installed on every experiment endpoint by provisioning. Runs the project payload (`run`) and serves `/health`,`/run`,`/status`,`/results`. Project-agnostic; the gate authors the payload.
- `src/khazad_dum/claude_sdk.py` — Agent SDK transport (`run_prompt`, `Mode.{TEXT,READ_ONLY,WRITE}`, `Result`, `ClaudeUnavailable`). Replaces the old `subprocess.run(["claude","-p",…])`; mode picks the tool/permission/system-prompt policy; `setting_sources` empty by default.
- `src/khazad_dum/steps.py` — ordered `STEPS` list; `Step` dataclass; `sub_prompts` wiring. (Current wiring lags the design — see roadmap.md.)
- `src/khazad_dum/state.py` — `.khazad-dum/state.json` read/write (`completed`, `current`, `sub_completed`).
- `src/khazad_dum/tokens.py` — tiktoken wrapper + `MAX_TOKENS`.
- `src/khazad_dum/terraform.py` — Terraform/AWS/1Password glue.
- `src/khazad_dum/workflows/<NN_slug>/{prompts,templates}/*.md` — the phase content (the active work area).
- `src/khazad_dum/workflows/research-planning-phase.md` — **global prompt** for Phase 1 (steps 1–4): the workflow tree + shared rules (non-interactive, never touch `input/`, scope/handoff). Each per-workflow prompt is appended after its trailing `THIS WORKFLOW IS:` line. (Not yet prepended by the builder — roadmap.md.)
- `src/khazad_dum/workflows/active-build-phase.md` — **global prompt** for Phase 2 (steps 5–6): Phase 2 tree + build rules (scope.md is the complete context, khazad-dum owns all git + the test gate, Rust only, tier-agnostic, report path). (Not yet prepended by the builder — roadmap.md.)
- `src/khazad_dum/terraform/` — packaged `.tf` skeleton synced into `~/.khazad-dum/terraform`.

## Commands
```bash
khazad-dum init                # scaffold documentation/ + .khazad-dum/state.json in CWD
khazad-dum                     # status (default)
khazad-dum run [slug|N]        # run next pending step (or named), --dry-run prints prompt
khazad-dum build experiment    # terraform apply: 2 endpoints (AWS + homelab) + listener + Twingate
khazad-dum start experiment    # trigger the run on each endpoint's listener (over Twingate)
khazad-dum fetch experiment    # pull results -> documentation/02_experiment/process/results/
khazad-dum graph experiment    # agent (WRITE): pandas/matplotlib -> output/graphs/
khazad-dum report experiment   # agent (WRITE): experiment report -> output/
khazad-dum destroy experiment  # terraform destroy them
khazad-dum tokens [file]       # token count (stdin if no file)
```
Experiment pipeline (fixed): **build → start → fetch → graph → report**.

## Conventions
- Don't trust README or `build/` for layout — trust `src/khazad_dum/workflows/` (both are stale; see roadmap.md).
- Workflow prompts are **non-interactive** (run via the Agent SDK) and never ask the user. **Phase 1** prompts write to `$CWD/documentation/<step>/{process,output}/` and **never** to `input/` (human-owned); shared rules live in `research-planning-phase.md`. **Phase 2** prompts edit the real project on a feature branch and write one report to `.khazad-dum/orchestration_log/<feature>/`; shared rules (no git, scope.md is the complete context, khazad-dum owns the gate, tier-agnostic) live in `active-build-phase.md`. Don't duplicate the global rules in each prompt.
- Every prompt's title must match its entry in its phase's global-prompt workflow tree, using the `Workflow x.x.x — <title>` (Phase.Step.Workflow) scheme, as a `##` heading (Phase 1 = `1.x.x` in `research-planning-phase.md`; Phase 2 = `2.x.x` in `active-build-phase.md`).
- **Phase 2 prompts are tier-agnostic:** never name a model or effort level — `khazad-dum` controls `--model`/`--effort` via the escalation ladder. And never tell a Phase 2 agent to run `git`.
