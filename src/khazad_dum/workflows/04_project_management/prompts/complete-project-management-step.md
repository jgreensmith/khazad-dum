## Workflow 1.4.2 — Complete Project Management Step

You run **when the human has decided (via the CLI) that the slicing is ready**. Using the current
`input/` plus the slice artifacts built up in `process/` and `documentation/features/`, finalise the
project breakdown for handoff to the Active Build phase.

You do **not** create git branches. `khazad-dum` creates them from the structured branch plan you
finalise here, once the plan is accepted. Your job is to produce that artefact and the finalised
plan. As always, **never modify `input/`**.

## Inputs (read-only)
- The provided **Project Description** — the detailed project description from the Architecture phase
  (iteration 4), as currently refined in `input/`.
- The **C4 diagram** and **DDD table** (with architectural layers) in `input/`.
- The `process/` artifacts: `feature-scopes.md`, `branch-plan.json`, and the
  `vertical-slicing-questionnaire-*.md` history.
- The per-feature scope docs at `documentation/features/*/scope.md`.

## Outputs

### 1 — Finalised feature-scopes table → `output/`
- `$CWD/documentation/04_project_management/output/feature-scopes.md` — the finalised ordered table.
  Refine the `process/` version into a clean, presentable handoff artifact (do not just copy it), and
  make sure every row's scope path and certainty are accurate against the final slices.

### 2 — Finalised project plan (iteration 5) → `output/`
- `$CWD/documentation/04_project_management/output/finalised-project-plan.md`. This is **iteration
  5**: the plan as it stands now that the work is broken into vertical slices. Synthesise the
  iteration-4 description with the final slicing — state the goal and scope, the **build order**, the
  **parallel-safe groupings**, how the slices add up to the whole system, and any decisions the build
  phase must still resolve. It is the direct input to the Active Build phase.

### 3 — Branch plan → `output/`
- `$CWD/documentation/04_project_management/output/branch-plan.json` — the finalised, accepted branch
  plan, refined from `process/branch-plan.json` (same shape). This is the artefact `khazad-dum` reads
  to create one git branch per slice. Ensure it is internally consistent: ordering matches the
  feature-scopes table, every `scope_path` exists under `documentation/features/`, and `depends_on`
  references resolve to real ids. **Do not run `git` yourself** — branch creation is a CLI action
  triggered on acceptance.

### 4 — Finalise the per-feature scope docs
- Ensure each `documentation/features/<feat-name>/scope.md` is complete and self-contained: a
  developer (human or agent) on that branch should be able to build and verify the slice from its
  scope doc alone. Do not move them — `documentation/features/` is their home for the build phase.
