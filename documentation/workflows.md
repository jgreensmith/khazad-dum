# Workflows (the phase content)

Location: `src/khazad_dum/workflows/<NN_slug>/{prompts,templates}/*.md`.
This is where the actual "what should the agent do each phase" lives. `01_research` is the
reference for quality/format; everything else is partial or stub.

## The 6 phases (`steps.py` STEPS)
NOTE: `steps.py` wiring still shows the OLD research chain; rewiring is deferred CLI work
(see CLAUDE.md "Deferred CLI work"). The "intended pattern" column is the new design.
| N | dir | intended pattern | prompt-file status |
|---|-----|------------------|--------------------|
| 1 | `01_research` | gate+complete (questionnaire loop) | **DONE** — reference example |
| 2 | `02_experiment` | gate+complete (questionnaire loop) | **DONE** — gate drafts `servers.json`+scripts to `process/`, human promotes to `input/`; uses infra (terraform.md) |
| 3 | `03_architecture` | loop+complete (**not** a certainty branch) | **DONE** — every cycle: questionnaire + C4 + DDD + skeleton proposal in `process/`; human advances; complete scaffolds skeleton in `$CWD` |
| 4 | `04_project_management` | loop+complete (**per-slice** certainty, not a branch) | **DONE** — every cycle: questionnaire + ordered feature-scopes table + per-feature scope docs + branch plan; complete finalises + emits `branch-plan.json` for the CLI to branch from |
| 5 | `05_developer_orchestration` | **deterministic TDD state machine** (9 phases, Phase 2) | **DONE** — see "Developer Orchestration" below |
| 6 | `06_delivery_and_maintenance` | single prompt (not a loop) | empty placeholder |

Conceptual grouping (from `workflows/research-planning-phase.md`, the global prompt): Phase 1 = Research/Plan (steps 1–4),
Phase 2 = Active Build (steps 5–6). All Phase 1 prompt titles match the global tree's `Workflow x.x.x`
scheme. The **questionnaire certainty loop applies to research and experiment**; **architecture uses a
different loop** (below).

## Gate+complete pattern (research, experiment)
Each = 2 sub-prompts:
1. **gate** (loops): reads `input/` → hard critical analysis (actively find problems) →
   self-assess % certainty. If <98 → write a NEW numbered questionnaire to `process/`
   (`...-questionnaire-{N}.md`, N = existing count + 1) and stop. If ≥98 → produce the phase
   deliverable. Gate files: research `literature-review-decision.md`, experiment `experiment-decision.md`.
2. **complete**: reads human-refined `input/` + the gate's deliverable → writes finalised
   handoff artifact(s) to `output/`. Files: `complete-research-step.md`, `complete-experiment-step.md`.

## Architecture loop+complete pattern (breaks the mould)
1. **loop** (`domain-modelling-loop.md`): NOT a certainty branch. Every cycle does BOTH — produce a
   fresh `domain-modelling-questionnaire-{N}.md` (initial questionnaire enforced) AND create/refine
   `c4-diagram.md` + `ddd-table.md` + `skeleton-proposal.md`, all in `process/`. No auto-advance;
   the human advances via the CLI when satisfied.
2. **complete** (`complete-architecture-step.md`): finalises C4 + DDD + `detailed-project-description.md`
   (iteration 4) to `output/`, **scaffolds the skeleton in `$CWD` root** (cargo workspace, structure
   only), and writes `test_commands` to `.khazad-dum/config.json`.

## Project Management loop+complete pattern (mirrors architecture)
1. **loop** (`vertical-slicing-loop.md`): like architecture, no global certainty branch — every cycle
   does BOTH: slice the **architectural-layers** table into the **narrowest** vertical slices, then
   produce a fresh `vertical-slicing-questionnaire-{N}.md`. Certainty is **per slice**: any slice
   <97% becomes a question. Each cycle creates/refines the ordered `process/feature-scopes.md` table,
   each `documentation/features/<feat-name>/scope.md` (**top-level**, outside the step dir — the build
   phase's unit of work), and the proposed `process/branch-plan.json`. Human advances via the CLI.
2. **complete** (`complete-project-management-step.md`): moves the table to `output/`, writes
   `finalised-project-plan.md` (iteration 5), and finalises `output/branch-plan.json`. The prompt
   **never runs git** — `khazad-dum` creates one branch per `branch-plan.json` entry on acceptance
   (CLI work, deferred), mirroring how `build` consumes `servers.json`.

## Developer Orchestration (step 05) — deterministic TDD state machine (Phase 2)
This is **Phase 2 (Active Build)**, not a planning phase, so it breaks every Phase 1 assumption:
- Its global prompt is **`workflows/active-build-phase.md`** (Phase 2 tree only — not steps 01–04).
- There is **no `documentation/05_*/{input,process,output}/`** plan to refine. The unit of work is one
  feature's `documentation/features/<feat>/scope.md` (authored by PM). Prompts edit the **real
  project** on a feature branch.
- **scope.md is the agent's complete context** — prompts forbid trawling/auditing the wider codebase
  (James's explicit requirement). Agents read only the modules scope.md names.

**Core split (what makes it deterministic):** agents write code + a status report; **`khazad-dum` is
the deterministic part** — after each agent run it executes the project's `test_commands` (from
`.khazad-dum/config.json`) as the *real* gate, owns all git, and drives every transition + escalation.
The agent's self-reported "tests pass" is never trusted.

**Nine phases** (`prompts/*-phase.md`, titled `Workflow 2.1.x`, all tier-agnostic). Numbering is a
stable id, so the two refactor phases (2.1.8/2.1.9) and diagnosis (2.1.7) are not in numeric order;
listed below in **execution** order:
1. `2.1.8 enabling-refactor-phase` — *optional, runs FIRST and only when scope.md's **Existing Code &
   Refactoring** section requires it.* Behaviour-preserving reshape of existing code so the feature
   fits ("make the change easy"). No new tests, no feature code. Gate: compiles + WHOLE existing
   suite still green + clippy + fmt; gets its own "tidy-first" commit before design.
2. `2.1.1 design-phase` — skeleton (modules/types/sigs, `todo!()` bodies). May add new types OR new
   methods/variants on existing types; never changes existing behaviour/signatures. Gate: `cargo build`.
3. `2.1.2 red-phase-e2e` — e2e/integration tests in the `e2e_tests` crate from scope's acceptance
   criteria. Gate: tests build + new tests fail + existing pass.
4. `2.1.3 red-phase-unit` — co-located `#[cfg(test)]` unit tests. Same red gate.
5. `2.1.4 red-review-phase` — review-only; scores **certainty** that the tests capture scope's e2e
   requirements + lists deficiencies (`review-report` template). Gate: certainty ≥ threshold → green;
   else → red-edit.
6. `2.1.5 red-edit-phase` — fixes the flagged tests only, stays red → back to 2.1.4 (loop, bounded).
7. `2.1.6 green-phase` — production code to pass ALL tests; never edits tests. Gate: all pass + clippy
   + fmt.
8. `2.1.9 cleanup-refactor-phase` — *runs AFTER green passes.* The classic TDD third beat: tidy this
   feature's code (dedup, extract, rename) behaviour-preservingly; a no-op is valid. Gate: prior green
   set unchanged + clippy + fmt.
9. `2.1.7 green-diagnosis-phase` — runs only when green exhausts the escalation ladder; emits a
   **verdict** `test-defect|scope-defect|impl-hard` (`diagnosis-report` template).

**Pipeline:** [enabling-refactor?] → design → red-e2e → red-unit → [red-review ↔ red-edit] → green →
[cleanup-refactor] → (on green exhaustion) diagnosis.

**Refactoring is behaviour-preserving only (for now)** — the shared rule lives in
`active-build-phase.md`; a slice that must *change* existing behaviour is routed to a human, so the
red gate's "existing tests still pass" invariant is never broken by a refactor. **Failure asymmetry:**
enabling-refactor fail → human (blocks); cleanup-refactor fail → revert to the green commit and
proceed (non-blocking — polish must not sink a passing feature).

**Escalation (config, never in prompts):** on a gate fail, retry at the same tier up to a budget, then
climb `haiku/medium → sonnet/medium → opus/high → human`. `khazad-dum` sets `--model`/`--effort`.

**Green-blocked routing = diagnose + bounded kickback:** top-tier green failure → 2.1.7 diagnosis →
`test-defect` kicks back to red-edit **once** (then human if still failing); `scope-defect`/`impl-hard`
→ human. This bounds any red↔green ping-pong.

**Git = khazad-dum only.** It checks out the branch, commits at each passed gate, pushes/PRs. Agents
never run git.

**Feedback templates** (`templates/`): `status-report.md` (all phases), `review-report.md` (2.1.4),
`diagnosis-report.md` (2.1.7). Each = a machine-readable ```json block (the routing signal) + prose
audit. All reports → `.khazad-dum/orchestration_log/<feature>/<workflow-id>-<slug>-{N}.md`.

(Wiring — steps.py `sub_prompts`, the orchestration state machine, escalation, git, config knobs — is
**deferred CLI work**; see CLAUDE.md. The old stale `prompts/refactor.md` has been deleted, superseded
by `enabling-refactor-phase.md` + `cleanup-refactor-phase.md`.)

Per-phase deliverables: research gate→literature review, complete→refined-project-plan +
experiment-recommendations. experiment gate→**draft** server config + provision scripts (`process/`,
human promotes to `input/`, which `build` reads), complete→finalised project plan (iter 3).
architecture loop→C4 + DDD + skeleton proposal (`process/`), complete→finalised C4 + DDD + detailed
project description (iter 4) + scaffolded skeleton + `test_commands`.

## How a step's files are used
- Single-prompt step → `prompts/prompt.md` (+ project `scope.md`).
- Multi-prompt step → one file per sub-prompt named exactly as in `steps.py` `sub_prompts`,
  run in order, each gated by `state.sub_completed`.
- Templates in `templates/` are injected only when registered in `cli._SUB_PROMPT_TEMPLATES`.
- `init` seeds the project's `input/scope.md` from the step's `scope_template_path`
  (`project-description.md` for sub-prompt steps, else `template.md`).

### Phase 1 prompt files (current, new pattern)
- research: `prompts/literature-review-decision.md` (gate) + `complete-research-step.md` (complete).
- experiment: `prompts/experiment-decision.md` (gate) + `complete-experiment-step.md` (complete).
  `prompts/summary.md` is separate — the build-time infra briefing, not a phase workflow.
- architecture: `prompts/domain-modelling-loop.md` (loop) + `complete-architecture-step.md` (complete).
- project management: `prompts/vertical-slicing-loop.md` (loop) + `complete-project-management-step.md` (complete).
- Obsolete questionnaire prompts (research pre/post, experiment pre) have been **deleted** (folded
  into the gates), not just pending. PM's empty `prompts/prompt.md` placeholder was also removed.

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
