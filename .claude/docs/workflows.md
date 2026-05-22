# Workflows (the phase content)

Location: `src/khazad_dum/workflows/<NN_slug>/{prompts,templates}/*.md`.
This is where the actual "what should the agent do each phase" lives. `01_research` is the
reference for quality/format; everything else is partial or stub.

## The 6 phases (`steps.py` STEPS)
| N | dir | sub_prompts | status |
|---|-----|-------------|--------|
| 1 | `01_research` | yes (4) | **complete** — use as the template for the rest |
| 2 | `02_experiment` | none wired | prompt files exist, not run; `experiment-decision.md` has TODOs; uses infra (terraform.md) |
| 3 | `03_architecture` | none | `prompts/prompt.md` empty placeholder |
| 4 | `04_project_management` | none | empty placeholder |
| 5 | `05_developer_orchestration` | none | empty placeholder |
| 6 | `06_delivery_and_maintenance` | none | empty placeholder |

Conceptual grouping (from `workflows/Global prompt.md`): Phase 1 = Research/Plan (steps 1–4),
Phase 2 = Active Build (steps 5–6).

## How a step's files are used
- Single-prompt step → `prompts/prompt.md` (+ project `scope.md`).
- Multi-prompt step → one file per sub-prompt named exactly as in `steps.py` `sub_prompts`,
  run in order, each gated by `state.sub_completed`.
- Templates in `templates/` are injected only when registered in `cli._SUB_PROMPT_TEMPLATES`.
- `init` seeds the project's `input/scope.md` from the step's `scope_template_path`
  (`project-description.md` for sub-prompt steps, else `template.md`).

### Research sub-prompt chain (the working example)
1. `create-pre-literature-review-questionnaire` (+ `questionnaire` template) → writes
   `process/pre-literature-review-questionnaire.md`
2. `literature-review-decision` (+ `literature-review` template) → self-assess **% certainty**;
   if <98 append more questions, if ≥98 write `output/literature-review.md`
3. `create-post-literature-review-questionnaire` (+ `questionnaire`) →
   `process/post-literature-review-questionnaire.md`
4. `next-steps` (no template) — **NOTE mismatch**: file on disk is `complete-research-step.md`,
   but `steps.py` lists `next-steps`. One of them must be renamed before this sub-prompt runs.

## Authoring conventions (distilled from 01_research — follow these)
- **Non-interactive.** Never instruct the agent to ask the user; outputs are file artifacts.
  State this intent (see `Global prompt.md`: "do not attempt to interact with the user",
  "treat your output as a handoff artefact, not final product").
- **Structure each prompt** as: `## Objective(s)` → `## Requirements` (with `####` sub-tasks)
  → an explicit **output file path** under `$CWD/documentation/<step>/{process|output}/...`.
- **process/ vs output/**: working/intermediate artifacts (questionnaires, configs, scripts)
  go in `process/`; finalized handoff artifacts (reviews, refined descriptions, plans) go in
  `output/`.
- **Certainty-gate pattern** for steps that produce something expensive: self-assess a
  percentage; below threshold (98) append clarifying questions instead of proceeding.
- **Reference injected material by name** ("the provided **template**", "**Project
  Description**") — these are appended under `## Template` / `## Scope` / `## Project
  Description` headings by the prompt builder.
- Citations (literature review): Obsidian-style `[Author, Year|source](URL)` + certainty &
  reliability tags with the 🟩/🟨/🟧/🟥 percentage bands. See `literature-review-decision.md`.

## To finish a phase
1. Write `prompts/prompt.md` (or named sub-prompt files).
2. If multi-prompt, add the `sub_prompts` tuple to its `Step(...)` in `steps.py`.
3. Fill its `templates/template.md` (or `project-description.md` + per-sub templates).
4. Register any injected templates in `cli._SUB_PROMPT_TEMPLATES`.
5. Define the input artifacts it reads and the output artifacts it writes (keep names
   consistent across phases — phase N output should feed phase N+1 input).

Cross-phase artifact handoffs are currently under-specified (e.g. experiment prompts mention
"Experiment Plan", "Project Plan - Iteration 2", "Experiment Report" with no defining
template). Pin these down when authoring.
