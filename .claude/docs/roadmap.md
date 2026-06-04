# Roadmap & project state (Claude)

The volatile project-state that used to live in CLAUDE.md: what's done, what's deferred, known gaps.
Durable per-step design is in [steps/](steps/); this file is the place for status/TODOs.

## Active work (as of 2026-05-22)
Authoring the phase **prompts** (the `.md` files under `workflows/`), **not** CLI code (deferred below).
Design = the human-in-control merged-gate model — see [workflows.md](workflows.md) and the
`[[khazad-dum-workflow-design]]` memory before editing prompts.

**Prompt-authoring status:** steps **01–05 DONE**; **06 not started** (deliverables undefined — needs
an interview with James first). After 06, the Deferred CLI work below is the remaining chunk (includes
the step-05 TDD orchestration engine).

**Next up:** author the step 06 prompts/templates (delivery & maintenance).

## Wiring reality vs design
`steps.py`: **research rewired (2026-06-04)** to `(research-gate, draft-and-refine,
complete-research-step)` with matching `_SUB_PROMPT_TEMPLATES`; experiment is wired
(`experiment-decision`, `complete-experiment-step`); architecture / PM / 05 / 06 still have **no**
`sub_prompts`. The per-step docs describe the **intended** design; the remaining rewires are deferred
(below). **Loop control** (per-gate re-run + human-gated advance) is still deferred for every step —
the linear runner walks each step's sub-prompts once.

## Deferred CLI work (do not do during prompt authoring unless asked)
The whole CLI surface is in flux — the goal is a bare interactive `khazad-dum` that shows status /
current step and offers the actions available for that step (replacing the `run` verb). Markdown is
authored CLI-agnostically (assumes the harness injects "cycle N" and that a human triggers the advance).

**DONE for experiment (2026-05-29), no longer deferred:** experiment `sub_prompts`;
`cli._SUB_PROMPT_TEMPLATES` experiment entries (gate→`questionnaire`, report→`experiment-report`);
the full `build→start→fetch→graph→report` pipeline (per-endpoint bundle staging, the packaged listener,
`tf_env()` injecting `TF_VAR_tg_*`). Loop control for the experiment gate is still part of the
interactive-CLI redesign.

Still deferred:
- **Prepend global prompts:** prepend `research-planning-phase.md` to every Phase 1 sub-prompt (steps
  1–4) and `active-build-phase.md` to every Phase 2 sub-prompt (steps 5–6), ahead of the per-workflow markdown.
- **Rewire `steps.py` `sub_prompts`:** ~~research~~ (done — `research-gate, draft-and-refine,
  complete-research-step`); architecture → `(domain-modelling-loop, complete-architecture-step)`; project_management →
  `(vertical-slicing-loop, complete-project-management-step)`; developer_orchestration → the 9 phase
  states (not a linear run-once chain). Switches arch/PM `scope_template_path` to `project-description.md`;
  their stub `template.md` can then go. **Step 05 has no single step `scope.md`** — it iterates over
  `documentation/features/<feat>/scope.md`; the orchestrator picks the feature and injects its scope.
- **Loop control:** the gate/loop sub-prompt (1.1.1 / 1.2.1 / 1.3.1 / 1.4.1) must re-run across cycles
  without auto-advancing; track the cycle count and inject "cycle N"; the human advances to the
  complete sub-prompt explicitly.
- **`cli._SUB_PROMPT_TEMPLATES`:** ~~research~~ (done — `research-gate`→`questionnaire`,
  `draft-and-refine`→`literature-review` + `questionnaire`); experiment
  gate → `questionnaire`; architecture loop → `questionnaire` + `c4-diagram` + `ddd-table` +
  `skeleton-proposal`, complete → `detailed-project-description`; PM loop → `questionnaire` +
  `feature-scopes` + `scope`. Step 05: every 2.1.x phase gets `status-report` except 2.1.4
  (`review-report`) and 2.1.7 (`diagnosis-report`); each phase also gets the selected feature's
  `scope.md` injected as its scope.
- **Step-05 TDD orchestration engine (the big chunk).** A deterministic state machine over the 2.1.x
  prompts: per-feature checkout → [enabling-refactor?] → design → red-e2e + red-unit → [red-review ↔
  red-edit] → green → [cleanup-refactor]; after each agent run run `test_commands` and route on the
  *real* result. Refactor gates (compiles + prior green set unchanged + clippy + fmt) and failure
  asymmetry (enabling → human; cleanup → revert to green commit, proceed). Escalation ladder
  haiku/medium → sonnet/medium → opus/high → human. Green-blocked → diagnosis → `test-defect` kicks
  back to red-edit once, else human; `scope-defect`/`impl-hard` → human. Git is khazad-dum's alone.
  All thresholds/budgets/ladder live in `.khazad-dum/config.json`; logs →
  `.khazad-dum/orchestration_log/<feature>/<workflow-id>-<slug>-{N}.md`. `init` creates
  `orchestration_log/` (or the orchestrator does on first run).
- **PM branch creation:** on plan acceptance, khazad-dum creates one git branch per entry in
  `documentation/04_project_management/output/branch-plan.json` (mirrors how `build` consumes
  `servers.json`). The prompt only emits the artefact.
- **`init` seeds `.khazad-dum/config.json`;** architecture's complete step writes `test_commands` into
  it (merge, don't clobber).
- **Already deleted (no longer pending):** research `create-pre/post-literature-review-questionnaire.md`
  + `literature-review-decision.md` (deleted 2026-06-04 in the research rewire),
  experiment `pre-experiment-questions.md` + `templates/experiment-plan.md`, architecture `prompts/prompt.md`,
  PM `prompts/prompt.md`, step-05 stale `prompts/refactor.md`.

## Known gaps (background)
- **README.md is stale:** documents an old `templates/prompts/NN.md` layout; real layout is
  `workflows/<NN_slug>/{prompts,templates}/`.
- **`build/`** holds the **old** layout — stale artifacts, not the source of truth.
- Steps 01–05 templates are complete; **06** still has a 3-line `templates/template.md` stub.
  Architecture + PM still carry an unused stub `templates/template.md` (active scope seed until their
  `sub_prompts` land, after which `project-description.md` takes over); experiment is wired and uses
  `project-description.md`.
- Stale human docs: `documentation/architecture.md` + `documentation/terraform.md` still describe the
  old `claude -p` subprocess and old `servers.json` schema (the `.claude/docs/` versions are current).

## Config
`.khazad-dum/config.json` is the per-project config (seeded by `init`, written by architecture's
complete step) holding `test_commands` for later phases; expected to grow other settings (step-05
thresholds/budgets/tier ladder).
