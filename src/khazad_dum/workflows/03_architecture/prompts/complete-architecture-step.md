## Workflow 1.3.2 — Complete Architecture Step

You run **when the human has decided (via the CLI) that the design is ready**. Using the current
`input/` plus the design artifacts built up in `process/`, finalise the architecture for handoff to
the Project Management phase, and scaffold the real project skeleton.

This is the one phase that writes **outside** `documentation/`: it scaffolds the project skeleton in
the `$CWD` root and records test commands in `.khazad-dum/config.json`. Even so, **never modify
`input/`**.

## Inputs (read-only)
- The provided **Project Description** — the finalised plan from the Experiment phase (iteration 3),
  as currently refined in `input/`.
- The `process/` artifacts: `c4-diagram.md`, `ddd-table.md`, `skeleton-proposal.md`, and the
  `domain-modelling-questionnaire-*.md` history.

## Outputs

### 1 — Finalised design docs (refined for presentation) → `output/`
- `$CWD/documentation/03_architecture/output/c4-diagram.md` — the finalised C4 diagram.
- `$CWD/documentation/03_architecture/output/ddd-table.md` — the finalised DDD table.
Refine the `process/` versions into clean, presentable handoff artifacts; do not just copy them.

### 2 — Detailed Project Description (iteration 4) → `output/`
- `$CWD/documentation/03_architecture/output/detailed-project-description.md`, using the provided
  **detailed project description template**.
- This is **iteration 4**: the most concrete description yet, sufficient for the Project Management
  phase to break the work into deliverables. Fold in the ubiquitous language, the C4 architecture,
  and the DDD model.

### 3 — Skeleton project → `$CWD` root
- Scaffold the project **structure only** per the approved `skeleton-proposal.md`: run the cargo
  scaffolding (e.g. `cargo new` / a cargo **workspace** with its member crates), create the directory
  and module layout, and lay down the **testing scaffolding** (test dirs/files and any test config).
- **Structure only — no business logic.** Stub modules and empty/`todo!()` test bodies are expected;
  do not implement features.

### 4 — Test commands → `.khazad-dum/config.json`
- Record the predetermined test commands under a `test_commands` key (a JSON array, e.g.
  `["cargo test"]`) so later phases can run them.
- If `.khazad-dum/config.json` already exists, **merge** this key in without clobbering other keys; if
  it does not exist, create it as a JSON object containing `test_commands`.
