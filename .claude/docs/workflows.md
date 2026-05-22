# Workflows (the phase content)

Location: `src/khazad_dum/workflows/<NN_slug>/{prompts,templates}/*.md`.
This is where the actual "what should the agent do each phase" lives. `01_research` is the
reference for quality/format; everything else is partial or stub.

## The 6 phases (`steps.py` STEPS)
NOTE: `steps.py` wiring still shows the OLD research chain; rewiring is deferred CLI work
(see CLAUDE.md "Deferred CLI work"). The "intended pattern" column is the new design.
| N | dir | intended pattern | prompt-file status |
|---|-----|------------------|--------------------|
| 1 | `01_research` | gate+complete (questionnaire loop) | **prompts rewritten to new pattern** — reference example |
| 2 | `02_experiment` | gate+complete (questionnaire loop) | TODO: rewrite to pattern; `experiment-decision.md` has TODOs; uses infra (terraform.md) |
| 3 | `03_architecture` | gate+complete (questionnaire loop) | TODO: empty placeholder; deliverables undefined |
| 4 | `04_project_management` | single prompt (not a loop) | empty placeholder |
| 5 | `05_developer_orchestration` | single prompt (not a loop) | empty placeholder |
| 6 | `06_delivery_and_maintenance` | single prompt (not a loop) | empty placeholder |

Conceptual grouping (from `workflows/research-planning-phase.md`, the global prompt): Phase 1 = Research/Plan (steps 1–4),
Phase 2 = Active Build (steps 5–6). The **questionnaire certainty loop applies only to research,
experiment, architecture**.

## Gate+complete pattern (research, experiment, architecture)
Each = 2 sub-prompts:
1. **gate** (loops): reads `input/` → hard critical analysis (actively find problems) →
   self-assess % certainty. If <98 → write a NEW numbered questionnaire to `process/`
   (`...-questionnaire-{N}.md`, N = existing count + 1) and stop. If ≥98 → produce the phase
   deliverable. Research gate file: `literature-review-decision.md`.
2. **complete**: reads human-refined `input/` + the gate's deliverable → writes finalised
   handoff artifact(s) to `output/`. Research complete file: `complete-research-step.md`.

Per-phase deliverables: research gate→literature review, complete→refined-project-plan +
experiment-recommendations. experiment gate→server config + provision scripts (`process/`,
read by `build`), complete→finalised project plan. architecture→TBD.

## How a step's files are used
- Single-prompt step → `prompts/prompt.md` (+ project `scope.md`).
- Multi-prompt step → one file per sub-prompt named exactly as in `steps.py` `sub_prompts`,
  run in order, each gated by `state.sub_completed`.
- Templates in `templates/` are injected only when registered in `cli._SUB_PROMPT_TEMPLATES`.
- `init` seeds the project's `input/scope.md` from the step's `scope_template_path`
  (`project-description.md` for sub-prompt steps, else `template.md`).

### Research files (current, new pattern)
- `prompts/literature-review-decision.md` = the gate.
- `prompts/complete-research-step.md` = the complete step.
- `prompts/create-pre-literature-review-questionnaire.md` + `create-post-literature-review-questionnaire.md`
  = **obsolete** (folded into the gate); pending deletion in the deferred CLI pass.

## Design intent (human-in-control) — see [[khazad-dum-workflow-design]] memory
AI does the heavy lifting; the human stays in control of the plan.
- **`input/` is human-owned. Prompts must NEVER write to or modify `input/`.** It holds the
  current plan iteration (research input = iter 1, experiment input = iter 2, …).
- **Questionnaire certainty cycle** (research, experiment, architecture): a fresh agent reads
  `input/` and either (a) is certain enough → produces the step's real output and the project
  advances; or (b) not certain → writes a **new questionnaire** to `process/` and stops. The
  human reads it, refines `input/` by hand, and re-runs. Repeat until a fresh agent clears the
  bar.
- **New questionnaire per cycle** — do NOT append to the existing questionnaire (this changes
  the original prompts, which said "append"). The CLI tracks the cycle count and injects
  "this is cycle N" into the prompt.

## Authoring conventions (distilled from 01_research — follow these)
- **Non-interactive.** Never instruct the agent to ask the user; outputs are file artifacts.
  These shared rules live once in the global prompt `research-planning-phase.md` (non-interactive,
  never touch `input/`, "treat your output as a handoff artefact, not final product") — don't repeat
  them in each Phase 1 prompt.
- **Structure each prompt** as: `## Objective(s)` → `## Requirements` (with `####` sub-tasks)
  → an explicit **output file path** under `$CWD/documentation/<step>/{process|output}/...`.
- **process/ vs output/**: working/intermediate artifacts (questionnaires, draft configs,
  scripts) go in `process/`; finalized handoff artifacts (reviews, refined descriptions,
  plans) go in `output/`. Never `input/`.
- **Certainty-gate pattern**: self-assess a percentage; below threshold (98) write a new
  clarifying questionnaire to `process/` instead of proceeding.
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
