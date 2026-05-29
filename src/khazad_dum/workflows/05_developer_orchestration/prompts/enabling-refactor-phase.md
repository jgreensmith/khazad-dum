## Workflow 2.1.8 — Enabling Refactor Phase

You run **before** any work begins on this feature, and **only** because its scope.md asks for it.
Some features cannot be added cleanly to the code that already exists — first you have to reshape
that code to make room. Your job is exactly that reshaping: a **behaviour-preserving** restructuring
of the existing code so the feature can be built on top of it without contortion. *Make the change
easy; the easy change comes later.* You add **no** feature behaviour and **no** tests.

## Inputs (read-only context)
- The provided **scope.md** — specifically its **Existing Code & Refactoring** section, which names
  the existing types/modules this slice touches and the enabling refactor it requires. That section
  is your worklist, and it also **bounds** what you may touch: read and reshape only the existing
  crates/modules it names.

## Requirements

#### Make the enabling refactor scope.md calls for
1. Carry out exactly the structural changes the **Existing Code & Refactoring** section describes —
   e.g. extract a trait or a seam so the new code can plug in, split an over-large function or
   struct, move code between modules, rename for clarity, introduce an abstraction the feature needs.
2. Keep every change **behaviour-preserving** — see the global "Refactoring is behaviour-preserving"
   rule. You are changing shape, not behaviour. Do **not** implement any part of the new feature
   (that is the Design and Green phases' job) and do **not** add new tests (that is the Red phases').
3. If a rename or signature/visibility change ripples into call sites, update them — including in
   existing tests — but **only mechanically**, never altering what a test asserts.

#### Stop if it is not really a refactor
- If the restructuring scope.md asks for cannot be done without changing existing behaviour, **do not
  do it**. Leave behaviour intact, change nothing risky, and report a blocker (the automated pipeline
  only performs behaviour-preserving refactoring; `khazad-dum` routes a behaviour change to a human).

#### Leave the ground green
- The workspace must still **compile** and the **entire existing test suite must still pass** — the
  same set of tests that passed before your run still passes after it, with none disabled or deleted.
  No new tests appear. (`khazad-dum` verifies with the project's build and test commands, plus
  `cargo clippy` and `cargo fmt`.)

Finish by writing your status report (status report template) to
`.khazad-dum/orchestration_log/<feature>/2.1.8-enabling-refactor-{N}.md` — name the restructuring you
performed, or, if you could not proceed behaviour-preservingly, record the blocker.
