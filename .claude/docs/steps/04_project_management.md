# Step 04 — Project Management (Claude)

Fourth (last) Phase-1 step. Cuts the layered architecture into the **narrowest vertical slices** —
each one feature, end-to-end — and produces the per-feature `scope.md` docs + branch plan that the
build phase consumes. Iteration 4 → PM output (iter 5). This is the **bridge out of input/process/output
into the real project.**

## Pattern
Loop + complete — mirrors Architecture (no global certainty branch). Every cycle does BOTH: refine the
slice artifacts AND emit a fresh questionnaire. Certainty is assessed **per slice**; any slice <97% ⇒
a question. Human advances via the CLI.

## Sub-prompts
- **1.4.1 `vertical-slicing-loop`** (loops): slice the **architectural-layers table** into thin
  end-to-end slices; classify each vs existing code (`new-only` / `extends-existing` /
  `requires-enabling-refactor`; behaviour-*changing* slices flagged human-led). Each cycle writes:
  `process/feature-scopes.md` (ordered table: slice → branch → scope path → parallel-safe → %certainty),
  one `documentation/features/<feat>/scope.md` per slice (**top-level**, the build phase's unit of
  work; includes an *Existing Code & Refactoring* section), `process/branch-plan.json`, and a new
  `vertical-slicing-questionnaire-{N}.md`.
- **1.4.2 `complete-project-management-step`** (human-triggered): finalise `output/feature-scopes.md`,
  `output/finalised-project-plan.md` (iter 5; build order + parallel-safe groupings),
  `output/branch-plan.json`, and ensure every `scope.md` is self-contained. **Never runs git** —
  khazad-dum creates one branch per `branch-plan.json` entry on acceptance.

## In → out
- **In:** `input/` detailed description (iter 4) + C4 + DDD (with layers table) + scaffolded skeleton.
- **Out:** `output/{feature-scopes.md,finalised-project-plan.md,branch-plan.json}`;
  `documentation/features/<feat>/scope.md` (one per slice). Working artifacts in `process/`.

## scope.md sections (the build-phase contract)
Summary · End-to-End Behaviour (per layer) · Acceptance Criteria · Contracts & Data · Dependencies ·
Out of Scope · **Existing Code & Refactoring**.

## Flow
loop cycle → (feature-scopes + per-feature scope.md + branch-plan + questionnaire) → human edits
`input/` → re-run … → human advances → complete → finalised table + plan + branch-plan.json →
khazad-dum creates branches.

## Key files
`workflows/04_project_management/prompts/{vertical-slicing-loop,complete-project-management-step}.md`;
templates `templates/{feature-scopes,scope,questionnaire,project-description}.md`.
