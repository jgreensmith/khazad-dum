## Workflow 1.3.1 — Domain Modelling Loop

You are a fresh agent entering the **Architecture** step. The goal of this phase is to produce
documentation that accurately defines and describes the application to be built.

This phase **breaks the usual gate pattern**. There is no certainty branch. On **every** cycle you do
**both**:
1. **refine the design artifacts** — the C4 diagram, the DDD table, and the skeleton project
   proposal, and
2. **produce a fresh questionnaire** that drives the next round of human input.

Everything you write stays in `process/`. Nothing advances automatically: the loop repeats until the
**human decides via the CLI** that the design is ready, at which point the Complete step (1.3.2) runs.
You never see the previous cycle's reasoning — only the current `input/` and the artifacts already in
`process/`.

## Inputs (read-only)
- The provided **Project Description** — the finalised project plan from the Experiment phase
  (iteration 3).
- Existing `process/` artifacts from prior cycles: previous questionnaires
  (`domain-modelling-questionnaire-*.md`), the current `c4-diagram.md`, `ddd-table.md`, and
  `skeleton-proposal.md`. Read them and **refine** them rather than starting from scratch.

## Step 1 — Determine the cycle
Count the questionnaire files in `process/` matching `domain-modelling-questionnaire-*.md`. The
current cycle `N` is that count **+ 1**. (If the harness has told you the cycle number, use that.)

## Step 2 — Drill into the domain model (do this hard)
Interrogate the plan and the existing artifacts. Actively hunt for gaps, ambiguities, and
contradictions across four fronts:
- **Ubiquitous language** — every domain term defined, disambiguated, and used consistently.
- **High-level technical architecture** — components/containers, their responsibilities and
  boundaries, data flow, interfaces/contracts, and the chosen tech stack (default **Rust / cargo
  workspace** unless the plan clearly requires otherwise) mapped onto the available infra (AWS EC2 +
  home lab).
- **Domain-driven design** — bounded contexts, aggregates, entities, value objects, domain events,
  and the invariants that protect them.
- **Layered architecture** — the horizontal layers (presentation/interface, application, domain,
  infrastructure) and exactly what lives in each. The **Project Management** phase (1.4) cuts
  *vertical* slices across these layers, so define them precisely now: every layer's responsibility
  and boundary must be clear enough that a single feature can be traced end-to-end through them.

## Step 3 — Create / refine the design artifacts (every cycle)
Write all three to `process/`. On cycle 1 these are first drafts; on later cycles, tweak them in
light of the newest `input/`. **Never write to `input/`.**
1. **C4 diagram** → `$CWD/documentation/03_architecture/process/c4-diagram.md`, using the provided
   **C4 template** (Mermaid `C4Context` + `C4Container`).
2. **DDD table** → `$CWD/documentation/03_architecture/process/ddd-table.md`, using the provided
   **DDD table template** — this covers the ubiquitous language, the DDD building blocks, **and the
   architectural-layers table** that the next phase slices vertically. Keep the layers table complete
   and current every cycle.
3. **Skeleton project proposal** → `$CWD/documentation/03_architecture/process/skeleton-proposal.md`,
   using the provided **skeleton proposal template**. Propose the project structure (cargo workspace
   layout — crates, directories, modules) and the **predetermined testing commands**. This is a
   **proposal only** — do **not** create any files outside `documentation/` in this step.

## Step 4 — Produce the questionnaire (ALWAYS — including the first cycle)
- Write a **new** file (never append/edit an existing one):
  `$CWD/documentation/03_architecture/process/domain-modelling-questionnaire-{N}.md`, using the
  provided **questionnaire template**.
- At the very top, record the **cycle number**.
- Turn the gaps from Step 2 — and any decision still unresolved in the artifacts from Step 3 — into
  4–12 hard domain-modelling questions. Prefer challenging questions that force the human to give
  **written** answers; other question types are allowed where they fit the template.

Stop here. The human refines `input/` and re-runs this loop, or decides via the CLI that the design
is ready and advances to the Complete step.
