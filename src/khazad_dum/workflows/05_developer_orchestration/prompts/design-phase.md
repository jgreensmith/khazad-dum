## Workflow 2.1.1 — Design Phase

The cargo workspace skeleton already exists (scaffolded by the Architecture phase). Using the
feature's **scope.md** as your complete specification, design the structural skeleton for **this
feature only**: the modules, types, traits, and method signatures it needs — with no behaviour. The
result must compile.

The feature may need brand-**new** types/modules, **new methods or variants on existing** types, or
(typically) both — adding a new `impl` method, a new enum variant, or a new trait impl to existing
code is expected and fine. What you must **not** do here is change the *behaviour* or *signatures* of
existing code. If existing code needed reshaping to host this feature, that has already happened in
the Enabling Refactor phase (2.1.8) that ran before you — build on its result.

## Inputs (read-only context)
- The provided **scope.md** for this feature — its Summary, End-to-End Behaviour (per layer),
  Acceptance Criteria, Contracts & Data, Dependencies, and Out of Scope. Design to it. Read only the
  existing crates/modules it names.

## Requirements

#### Design the feature's structure
1. Lay out the module / struct / trait hierarchy this feature requires (data models, services,
   handlers, error types) and place each in the correct existing crate and module per scope.md.
2. Define types with appropriate fields and visibility (`pub`/private, owned/borrowed), and the
   trait boundaries that make the feature testable and its dependencies substitutable.
3. Add `impl` blocks exposing the full public API the scope's behaviour and **Contracts & Data**
   imply — correct names, parameters, and return/error types.
4. Define the feature's error type(s) and how they surface to callers.

#### Leave all behaviour unimplemented
- New method bodies are placeholders only: `todo!()` or `unimplemented!()`. No logic, no control
  flow, no I/O.
- Add **only** the new code this feature needs — new items, or new methods/variants/impls on
  existing types, count as adding. Do **not** delete, rewrite, or change the behaviour or signatures
  of existing code, and do **not** add or modify any tests — tests come in the Red phases.

#### Must compile
- The skeleton must build cleanly. Get signatures, imports, and module wiring correct enough that the
  workspace compiles with placeholder bodies. (`khazad-dum` verifies with the project's build
  command.)

Finish by writing your status report (status report template) to
`.khazad-dum/orchestration_log/<feature>/2.1.1-design-{N}.md`.
