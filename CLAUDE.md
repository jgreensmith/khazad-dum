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

## Known gaps (as of 2026-05-22)
- README.md is **stale**: documents an old `templates/prompts/NN.md` layout; real layout is `workflows/<NN_slug>/{prompts,templates}/`.
- `build/` holds the **old** layout — stale artifacts, not the source of truth.
- `steps.py` research `sub_prompts` references `next-steps`, but the file is `complete-research-step.md` (mismatch).
- Experiment (`02_experiment`) has prompt files but `Step(2)` has **no `sub_prompts`**, so they never run.
- `03`–`06` `prompts/prompt.md` are empty placeholders; all `templates/template.md` except `01_research` are stubs.
- Only `01_research/templates/*` are considered correct/complete.

## Conventions
- Don't trust README or `build/` for layout — trust `src/khazad_dum/workflows/`.
- Workflow prompts are non-interactive (`claude -p`); they must write outputs to files under `$CWD/documentation/<step>/{process,output}/`, never ask the user.
