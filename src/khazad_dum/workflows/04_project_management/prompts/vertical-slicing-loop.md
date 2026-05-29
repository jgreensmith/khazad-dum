## Workflow 1.4.1 — Vertical Slicing Loop

You are a fresh agent entering the **Project Management** step. The goal of this phase is to split the
layered architecture into the **narrowest possible vertical slices** — each slice one feature
delivered end-to-end, with confirmed end-to-end requirements, ready to become an actionable branch in
the build phase. This is the bridge out of the input/process/output planning model and into the real
project.

This phase **breaks the usual gate pattern** (it mirrors the Architecture loop). There is no global
certainty branch. On **every** cycle you do **both**:
1. **refine the slice artifacts** — the ordered feature-scopes table, the per-feature scope docs, and
   the proposed branch plan, and
2. **produce a fresh questionnaire** that drives the next round of human input.

Certainty is assessed **per slice**: for each slice, how confident are you that you understand its
end-to-end requirements? Any slice below **97%** must be turned into a question in this cycle's
questionnaire.

Everything you write stays in `process/`, except the per-feature scope docs (which live at top-level
`documentation/features/<feat-name>/scope.md` — the unit of work for the build phase). Nothing
advances automatically: the loop repeats until the **human decides via the CLI** that the slicing is
ready, at which point the Complete step (1.4.2) runs. You never see the previous cycle's reasoning —
only the current `input/` and the artifacts already in `process/` and `documentation/features/`.

## Inputs (read-only)
- The provided **Project Description** — the detailed project description from the Architecture phase
  (iteration 4).
- The **C4 diagram** and **DDD table** (including its **architectural-layers table**) promoted into
  `input/` from the Architecture phase. The layers table is the horizontal grid you cut vertical
  slices against.
- The scaffolded **skeleton project** in the `$CWD` root (structure only — crates/modules/tests).
- Existing artifacts from prior cycles: `process/feature-scopes.md`, `process/branch-plan.json`,
  previous questionnaires (`vertical-slicing-questionnaire-*.md`), and the existing
  `documentation/features/*/scope.md`. Read them and **refine** them rather than starting from
  scratch.

## Step 1 — Determine the cycle
Count the questionnaire files in `process/` matching `vertical-slicing-questionnaire-*.md`. The
current cycle `N` is that count **+ 1**. (If the harness has told you the cycle number, use that.)

## Step 2 — Vertically slice the layered architecture (do this hard)
Take the **architectural-layers table** from the DDD doc and cut the system into the **narrowest**
vertical slices you can justify. A slice is a thin end-to-end path through the layers it touches
(presentation → application → domain → infrastructure) that delivers **one** coherent, independently
buildable and testable piece of behaviour.
- **Slice as narrowly as possible** — prefer many small slices over a few large ones. If a slice can
  be split without breaking end-to-end coherence, split it.
- For **each slice, confirm the end-to-end requirements**: exactly what it adds or changes at every
  layer it touches, its acceptance criteria, and the contracts/data it produces and consumes.
- Map **dependencies and conflicts** between slices: which must be built in series (one depends on
  another), and which are **parallel-safe** (no ordering dependency and no overlapping
  files/modules, so two branches could be worked at once without conflict).
- **Classify each slice against existing code.** Decide whether it is `new-only`, `extends-existing`
  (adds methods/variants/impls to existing types without changing them), or
  `requires-enabling-refactor` (existing code must be **behaviour-preservingly** reshaped first so
  the slice fits). Note the existing types/modules it touches and the enabling refactor it needs. If
  a slice would have to **change existing behaviour** (not just structure), flag it as **human-led** —
  the build phase only performs behaviour-preserving refactoring, so prefer to slice such that any
  behaviour change is isolated and explicitly flagged.
- **Self-assess certainty per slice** (0–100%): your confidence that you understand that slice's
  end-to-end requirements **and its impact on existing code** (what it extends, and any enabling
  refactor it needs). Below **97%** ⇒ it must be queried in this cycle's questionnaire.

## Step 3 — Create / refine the slice artifacts (every cycle)
On cycle 1 these are first drafts; on later cycles, refine them in light of the newest `input/`.
**Never write to `input/`.**
1. **Ordered feature-scopes table** → `$CWD/documentation/04_project_management/process/feature-scopes.md`,
   using the provided **feature scopes template**. Order by build order (respecting dependencies);
   each row points to the slice's `documentation/features/<feat-name>/scope.md` and records its
   parallel-safety and **% certainty**.
2. **Per-feature scope docs** → `$CWD/documentation/features/<feat-name>/scope.md` (one directory per
   slice), using the provided **feature scope template**. Capture the exact end-to-end requirements so
   the slice can be built and verified from this file alone — including its **Existing Code &
   Refactoring** section (relationship to existing code, the types/modules it touches, and any
   behaviour-preserving enabling refactor it needs before the feature). These live outside
   `documentation/04_*/` on purpose — they are the hand-off into the real project.
3. **Proposed branch plan** → `$CWD/documentation/04_project_management/process/branch-plan.json`, a
   machine-readable list of the proposed branches (one per slice) that `khazad-dum` will create when
   the human accepts the plan. This is a **proposal only** — do **not** run any `git` commands or
   create branches yourself. Use this shape:
   ```json
   {
     "branches": [
       {
         "id": "01-<slug>",
         "name": "<human-readable slice name>",
         "branch": "feat/<slug>",
         "scope_path": "documentation/features/<feat-name>/scope.md",
         "depends_on": ["<id>", "..."],
         "certainty": 0
       }
     ]
   }
   ```
   Keep `branches` ordered by build order and consistent with the feature-scopes table.

## Step 4 — Produce the questionnaire (ALWAYS — including the first cycle)
- Write a **new** file (never append/edit an existing one):
  `$CWD/documentation/04_project_management/process/vertical-slicing-questionnaire-{N}.md`, using the
  provided **questionnaire template**.
- At the very top, record the **cycle number**.
- Turn **every slice below 97% certainty** into a hard question about that slice's end-to-end
  requirements, plus any unresolved slicing or dependency/parallelism decisions. Aim for 4–12
  questions. Prefer challenging questions that force the human to give **written** answers; other
  question types are allowed where they fit the template.

Stop here. The human refines `input/` and re-runs this loop, or decides via the CLI that the slicing
is ready and advances to the Complete step.
