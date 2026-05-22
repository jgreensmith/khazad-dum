# khazad-dum — Agent Index

Python CLI that wraps the `claude` CLI to drive a project through 6 phases. Each `run`
assembles a prompt from packaged workflow markdown + the project's `scope.md`, token-checks
it (tiktoken `cl100k_base`, 180k limit), then shells out to `claude -p`. A `build`/`destroy`
pair provisions AWS EC2 experiment servers via Terraform.

**This file is an index. Read the linked doc only when working in that area — do not load all of them.**

## Docs (read on demand)
- [.claude/docs/architecture.md](.claude/docs/architecture.md) — module map, prompt-assembly data flow, state model.
- [.claude/docs/workflows.md](.claude/docs/workflows.md) — the 6-phase model, sub-prompt wiring, `workflows/` file layout, **authoring conventions for prompts/templates**.
- [.claude/docs/terraform.md](.claude/docs/terraform.md) — `build`/`destroy`, TF home, 1Password creds, MinIO state backend, regions.

## Source map
- `src/khazad_dum/cli.py` — argparse entry (`main`); commands: `init`, `status` (default), `run`, `build`, `destroy`, `tokens`.
- `src/khazad_dum/steps.py` — ordered `STEPS` list; `Step` dataclass; `sub_prompts` wiring.
- `src/khazad_dum/state.py` — `.khazad-dum/state.json` read/write (`completed`, `current`, `sub_completed`).
- `src/khazad_dum/tokens.py` — tiktoken wrapper + `MAX_TOKENS`.
- `src/khazad_dum/terraform.py` — Terraform/AWS/1Password glue.
- `src/khazad_dum/workflows/<NN_slug>/{prompts,templates}/*.md` — the phase content (the active work area).
- `src/khazad_dum/workflows/research-planning-phase.md` — **global prompt** for the first 4 steps (Phase 1: research, experiment, architecture, project management). Holds the workflow tree + shared rules (non-interactive, never touch `input/`, scope/handoff) so individual prompts don't repeat them. Each per-workflow prompt is appended after its trailing `THIS WORKFLOW IS:` line. NOTE: not yet prepended by the prompt builder — see Deferred CLI work.
- `src/khazad_dum/terraform/` — packaged `.tf` skeleton synced into `~/.khazad-dum/terraform`.

## Commands
```bash
khazad-dum init                # scaffold documentation/ + .khazad-dum/state.json in CWD
khazad-dum                     # status (default)
khazad-dum run [slug|N]        # run next pending step (or named), --dry-run prints prompt
khazad-dum build experiment    # terraform apply experiment servers
khazad-dum destroy experiment  # terraform destroy them
khazad-dum tokens [file]       # token count (stdin if no file)
```

## Active work: authoring workflow prompts (as of 2026-05-22)
Goal of current effort = write the phase prompts (the `.md` files), **not** CLI code (deferred).
Design is the human-in-control merged-gate model — read [.claude/docs/workflows.md](.claude/docs/workflows.md) §"Design intent" and the `[[khazad-dum-workflow-design]]` memory before editing prompts.

**Next up (where to resume):** author the **steps 05–06** prompts/templates (dev orchestration, delivery) — single-prompt phases, NOT questionnaire loops. Their deliverables are **undefined** and will need an interview with James first (as architecture/PM did). After authoring, the **Deferred CLI work** block below is the other outstanding chunk.

Progress:
- **01_research — DONE (new pattern).** `prompts/literature-review-decision.md` = Workflow 1.1.1, the looping gate (critical analysis → certainty branch → new numbered questionnaire in `process/` OR literature review in `output/`). `prompts/complete-research-step.md` = Workflow 1.1.2, reads refined `input/` + lit review → writes `refined-project-plan.md` + `experiment-recommendations.md` (constrained to EC2 + home lab).
- **02_experiment — DONE (gate+complete).** `prompts/experiment-decision.md` = Workflow 1.2.1, looping gate (critical analysis → certainty branch → new numbered questionnaire OR **draft** `servers.json` + provision scripts + `PROMOTION.md` in `process/`). `prompts/complete-experiment-step.md` = Workflow 1.2.2, writes `finalised-project-plan.md` (iteration 3) to `output/`. Handoff: agent drafts config to `process/`, **human promotes to `input/`**, `build` reads `input/` (unchanged). `pre-experiment-questions.md` folded into the gate (deleted).
- **03_architecture — DONE (loop+complete, breaks the mould).** `prompts/domain-modelling-loop.md` = Workflow 1.3.1: **every** cycle produces BOTH a fresh questionnaire AND refines `c4-diagram.md` + `ddd-table.md` + `skeleton-proposal.md`, all in `process/`; no certainty branch, human advances via CLI. `prompts/complete-architecture-step.md` = Workflow 1.3.2: finalises C4 + DDD + `detailed-project-description.md` (iteration 4) to `output/`, **scaffolds the skeleton project in `$CWD` root** (cargo workspace, structure only), and writes `test_commands` to `.khazad-dum/config.json`. Stack default = Rust/cargo.
- **04_project_management — DONE (loop+complete, mirrors architecture; supersedes the old "single prompt" intent).** `prompts/vertical-slicing-loop.md` = Workflow 1.4.1: every cycle slices the **architectural-layers** table into the **narrowest vertical slices**, refines the ordered `process/feature-scopes.md` table (slice → branch → scope path → parallel-safe → **per-slice % certainty**, <97% ⇒ question), writes each `documentation/features/<feat-name>/scope.md` (**top-level** — the bridge out of IPO, the build phase's unit of work), drafts `process/branch-plan.json`, and emits a questionnaire. `prompts/complete-project-management-step.md` = Workflow 1.4.2: moves the table to `output/`, writes `finalised-project-plan.md` (iteration 5), finalises `output/branch-plan.json`. **Branch creation itself is done by `khazad-dum`** reading `output/branch-plan.json` (CLI work, deferred) — the prompt never runs git. Templates: `feature-scopes.md`, `scope.md`, `project-description.md` (iter-4 seed), `questionnaire.md`.
- **05–06 — not started:** `prompts/prompt.md` are empty placeholders (dev orchestration, delivery — these are NOT questionnaire-loop phases).

Iteration model (plan handoff): research input = iter 1 → research output / experiment input = iter 2 → experiment output / architecture input = iter 3 → architecture output (`detailed-project-description.md`) = iter 4 / PM input → PM output (`finalised-project-plan.md`) = iter 5 → Active Build.
`.khazad-dum/config.json` is a new project config (seeded by `init`, written by architecture's complete step) holding `test_commands` for later phases; expected to grow to hold other project settings.

## Deferred CLI work (do not do during prompt authoring unless asked)
The whole CLI command surface is **in flux** — the goal is a bare interactive `khazad-dum` that shows status / current step and offers the actions available for that step (replacing the `run` verb). Wire the items below into whatever that becomes; the prompt/template markdown is authored CLI-agnostically (assumes the harness injects "cycle N" and that a human triggers the advance).
- Prepend `research-planning-phase.md` (the global prompt) to every Phase 1 (steps 1–4) sub-prompt in the prompt builder, ahead of the per-workflow markdown.
- Rewire `steps.py` `sub_prompts`: research → `("literature-review-decision", "complete-research-step")`; experiment → `("experiment-decision", "complete-experiment-step")`; architecture → `("domain-modelling-loop", "complete-architecture-step")`; project_management → `("vertical-slicing-loop", "complete-project-management-step")`. (This switches experiment + architecture + PM `scope_template_path` to their new `project-description.md`; their stub `template.md` can then go.)
- Loop control: the gate/loop sub-prompt (research 1.1.1, experiment 1.2.1, architecture 1.3.1, PM 1.4.1) must **re-run across cycles** without auto-advancing; track cycle count and inject "cycle N"; the human advances to the complete sub-prompt explicitly (an action in the interactive UI).
- Update `cli._SUB_PROMPT_TEMPLATES`: research gate needs `questionnaire` + `literature-review`; experiment gate needs `questionnaire`; architecture loop needs `questionnaire` + `c4-diagram` + `ddd-table` + `skeleton-proposal`; architecture complete needs `detailed-project-description`; PM loop needs `questionnaire` + `feature-scopes` + `scope`.
- **PM branch creation:** when the human accepts the PM plan, `khazad-dum` creates one git branch per entry in `documentation/04_project_management/output/branch-plan.json` (mirrors how `build` consumes `servers.json`). The prompt only emits the artefact — it never runs git.
- `init` must seed `.khazad-dum/config.json`; architecture's complete step writes `test_commands` into it (merge, don't clobber).
- Already deleted during authoring (no longer pending): research `create-pre/post-literature-review-questionnaire.md`, experiment `pre-experiment-questions.md` + `templates/experiment-plan.md`, architecture `prompts/prompt.md`, PM `prompts/prompt.md`.
- Fix `next-steps` vs `complete-research-step.md` name mismatch via the rewire above.

## Known gaps (background)
- README.md is **stale**: documents an old `templates/prompts/NN.md` layout; real layout is `workflows/<NN_slug>/{prompts,templates}/`.
- `build/` holds the **old** layout — stale artifacts, not the source of truth.
- `01_research`–`04_project_management` templates are complete; phases 05–06 still have 3-line `templates/template.md` stubs. Experiment + architecture + PM still carry an unused stub `templates/template.md` (the active scope seed until `steps.py` gets their `sub_prompts`, after which `project-description.md` takes over).

## Conventions
- Don't trust README or `build/` for layout — trust `src/khazad_dum/workflows/`.
- Workflow prompts are non-interactive (`claude -p`); they write outputs to files under `$CWD/documentation/<step>/{process,output}/` and **never** to `input/` (human-owned) and never ask the user. For Phase 1 these shared rules live in the global prompt (`research-planning-phase.md`) — don't duplicate them in each prompt.
- Each Phase 1 prompt's title must match its entry in the global prompt's workflow tree, using the `Workflow x.x.x — <title>` (Phase.Step.Workflow) scheme, as a `##` heading.
