# Workflows — the 6-phase model (Claude)

The "intelligence" of khazad-dum lives in packaged markdown under
`src/khazad_dum/workflows/<NN_slug>/{prompts,templates}/*.md`, assembled into a prompt and run through
the Agent SDK (see [architecture.md](architecture.md)). Per-step detail is in
[steps/](steps/) — read the one you need. Project state / deferred wiring is in [roadmap.md](roadmap.md).

## Two phases
- **Phase 1 — Research & Planning (steps 1–4).** Global prompt `workflows/research-planning-phase.md`
  (workflow tree + shared rules: non-interactive, never write `input/`, output = handoff artefact).
  Each step writes to `$CWD/documentation/<step>/{process,output}/`; **`input/` is human-owned**.
- **Phase 2 — Active Build (steps 5–6).** Global prompt `workflows/active-build-phase.md`. Agents edit
  the real project on a feature branch and write one report to `.khazad-dum/orchestration_log/`;
  khazad-dum owns git + the test gate; tier-agnostic.

## The six steps
| N | step | pattern | see |
|---|------|---------|-----|
| 1 | research | gate + complete (certainty loop) | [steps/01](steps/01_research.md) |
| 2 | experiment | gate + complete + `build→start→fetch→graph→report` | [steps/02](steps/02_experiment.md) |
| 3 | architecture | loop + complete (no certainty branch); scaffolds skeleton | [steps/03](steps/03_architecture.md) |
| 4 | project_management | loop + complete (per-slice certainty); emits scope.md + branch-plan | [steps/04](steps/04_project_management.md) |
| 5 | developer_orchestration | deterministic 9-phase TDD state machine | [steps/05](steps/05_developer_orchestration.md) |
| 6 | delivery_and_maintenance | single prompt (not started) | [steps/06](steps/06_delivery_and_maintenance.md) |

## Patterns
- **Gate + complete** (1, 2): a fresh agent reads `input/`, self-assesses % certainty; <threshold →
  writes a NEW numbered questionnaire to `process/` and stops; ≥threshold → produces the deliverable.
  The human refines `input/` by hand between cycles and re-runs. The **complete** sub-prompt then
  writes the finalised handoff to `output/`.
- **Loop + complete** (3, 4): no certainty *branch* — every cycle produces BOTH refined artifacts AND a
  fresh questionnaire; the human advances explicitly via the CLI. (PM gates per-slice at 97%.)
- **TDD state machine** (5): deterministic; khazad-dum routes on the *real* test result, not the
  agent's self-report.

## Iteration model (plan handoff)
research input = iter 1 → research output / experiment input = iter 2 → experiment output / architecture
input = iter 3 → architecture output (`detailed-project-description.md`) = iter 4 / PM input → PM
output (`finalised-project-plan.md`) = iter 5 → Active Build.

## Authoring conventions
- Title each prompt `## Workflow x.x.x — <title>`, matching its phase's global-prompt tree
  (Phase 1 = `1.x.x`; Phase 2 = `2.x.x`).
- `## Objective(s)` → `## Requirements` (`####` sub-tasks) → explicit output path under
  `documentation/<step>/{process|output}/`. Reference injected material by name (**Project
  Description**, **Template**).
- `process/` = working/intermediate; `output/` = finalised handoff; **never `input/`**.
- Don't repeat the global-prompt rules in each step prompt.
- Phase 2 prompts: tier-agnostic (never name a model/effort) and never tell an agent to run git.
