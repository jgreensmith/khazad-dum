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

Progress:
- **01_research — DONE (new pattern).** `prompts/literature-review-decision.md` = Workflow 1.1.1, the looping gate (critical analysis → certainty branch → new numbered questionnaire in `process/` OR literature review in `output/`). `prompts/complete-research-step.md` = Workflow 1.1.2, reads refined `input/` + lit review → writes `refined-project-plan.md` + `experiment-recommendations.md` (constrained to EC2 + home lab).
- **02_experiment — TODO:** rewrite to gate+complete pattern (gate certain-output = server config + provision scripts in `process/`, which `build` reads; complete = finalised project plan in `output/`). `experiment-decision.md` still has TODOs.
- **03_architecture — TODO:** same gate+complete pattern; deliverables not yet defined (interview pending).
- **04–06 — not started:** `prompts/prompt.md` are empty placeholders (PM, dev orchestration, delivery — these are NOT questionnaire-loop phases).

## Deferred CLI work (do not do during prompt authoring unless asked)
- Prepend `research-planning-phase.md` (the global prompt) to every Phase 1 (steps 1–4) sub-prompt in the prompt builder, ahead of the per-workflow markdown.
- Rewire `steps.py` `sub_prompts`: research → `("literature-review-decision", "complete-research-step")`; add experiment + architecture tuples.
- The gate sub-prompt must be allowed to **loop** (re-run same sub-prompt across cycles); CLI must track cycle count and inject "cycle N" into the prompt.
- Update `cli._SUB_PROMPT_TEMPLATES`: research gate now needs **both** `questionnaire` + `literature-review` templates injected.
- Delete obsolete files: `01_research/prompts/create-pre-literature-review-questionnaire.md` and `create-post-literature-review-questionnaire.md` (folded into the gate).
- Fix `next-steps` vs `complete-research-step.md` name mismatch via the rewire above.

## Known gaps (background)
- README.md is **stale**: documents an old `templates/prompts/NN.md` layout; real layout is `workflows/<NN_slug>/{prompts,templates}/`.
- `build/` holds the **old** layout — stale artifacts, not the source of truth.
- Only `01_research/templates/*` are correct/complete; other phases' `templates/template.md` are 3-line stubs.

## Conventions
- Don't trust README or `build/` for layout — trust `src/khazad_dum/workflows/`.
- Workflow prompts are non-interactive (`claude -p`); they write outputs to files under `$CWD/documentation/<step>/{process,output}/` and **never** to `input/` (human-owned) and never ask the user. For Phase 1 these shared rules live in the global prompt (`research-planning-phase.md`) — don't duplicate them in each prompt.
- Each Phase 1 prompt's title must match its entry in the global prompt's workflow tree, using the `Workflow x.x.x — <title>` (Phase.Step.Workflow) scheme, as a `##` heading.
