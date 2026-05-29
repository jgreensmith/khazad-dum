# Architecture

## Runtime shape
`khazad-dum` is a thin orchestrator. It does not call any model API directly — it builds a
text prompt and drives Claude through the **Agent SDK** (`claude_sdk.run_prompt`), which runs
the locally installed `claude` binary under subscription/CLI auth (no `ANTHROPIC_API_KEY`).
All "intelligence" lives in the packaged workflow markdown, not in Python.

`claude_sdk.py` wraps the SDK's async `query()` and exposes a `Mode` that scopes tool access
per call: `TEXT` (no tools, no ambient config — answer from the prompt alone, e.g.
questionnaires/summaries), `READ_ONLY` (Read/Glob/Grep, no mutation — review/analysis), and
`WRITE` (full coding with bypassed permission prompts — Phase 2 build work). It streams the
agent's text/tool activity to stdout and returns a `Result{text, is_error, subtype, num_turns,
cost_usd}`. `setting_sources` defaults to empty so ambient `CLAUDE.md`/settings/skills never
leak into a run — the assembled prompt is the whole context.

## Two state locations
1. **Per-project** (in CWD): `documentation/` (the work product) + `.khazad-dum/state.json`
   (progress). Created by `init`. A symlink `~/Notes/Projects/<dirname> -> ./documentation`
   is added so docs are editable from Obsidian.
2. **Global** (`~/.khazad-dum/terraform/`): the writable Terraform home — see terraform.md.

## Prompt-assembly data flow (`run`)
`cli.cmd_run` →
- pick step: explicit arg via `steps.get_step`, else `_next_pending(state)`.
- if step has `sub_prompts`: pick next unfinished via `_next_pending_sub_prompt`, build with
  `_build_sub_prompt`; else build with `_build_prompt`.
- **`_build_prompt`** = `workflows/<dir>/prompts/prompt.md` + the project's
  `documentation/<dir>/input/scope.md` (appended under a `## Scope` heading).
- **`_build_sub_prompt`** = `workflows/<dir>/prompts/<sub>.md` + project `scope.md` (as
  `## Project Description`) + any templates listed in `cli._SUB_PROMPT_TEMPLATES[sub]`
  (appended under `## Template`).
- `tokens.assert_within_limit` (180k, `cl100k_base`) — raises if over.
- `--dry-run` prints the assembled prompt and stops.
- otherwise set `state.current`, run the prompt via `_invoke` → `claude_sdk.run_prompt`
  (WRITE mode, `cwd=project_root`), and when the `Result` is not an error mark
  sub/step complete in `state.json`.

`_SUB_PROMPT_TEMPLATES` (in cli.py) is the map of which template files get injected into each
research sub-prompt. New templated sub-prompts must be registered there.

## State model (`state.py`)
`State{ completed: list[str], current: str|None, sub_completed: dict[str, list[str]] }`,
keyed by `step.dir_name` (e.g. `01_research`). `mark_completed` clears `current`;
`mark_sub_completed` appends to the per-step sub list. A step with `sub_prompts` is marked
complete by `cmd_run` once its last sub-prompt finishes.

## Step model (`steps.py`)
`Step{ index, slug, name, sub_prompts }`. `dir_name = f"{index:02d}_{slug}"`.
`scope_template_path` points at `templates/project-description.md` when the step has
sub_prompts, else `templates/template.md`. `get_step` accepts an int, a numeric string, a
slug, or a full dir_name.

## Packaging
`pyproject.toml` ships `workflows/**/*.md` and the `terraform/` tree as package-data;
`cli._template_text` / `terraform.ensure_tf_home` read them via `importlib.resources`.
So workflow/template edits only take effect after a reinstall unless installed editable
(`pipx install --editable .`).
