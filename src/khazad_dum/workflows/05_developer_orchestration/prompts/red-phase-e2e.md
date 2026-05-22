## Workflow 2.1.2 — Red Phase: End-to-End Tests

The feature skeleton compiles with unimplemented bodies. Write the **end-to-end / integration
tests** that pin down the feature's externally observable behaviour, taken straight from scope.md.
These are the outer specification the Green phase must satisfy. Write **no production code**.

## Inputs (read-only context)
- The provided **scope.md** — drive the tests from its **End-to-End Behaviour** and **Acceptance
  Criteria**, and the **Contracts & Data** the feature exposes.
- The compiling skeleton from the Design phase — assert against its real signatures.

## Requirements

#### Write the e2e tests
1. Place integration tests in the `e2e_tests` crate, one file per coherent workflow/scenario, each
   named for the behaviour it exercises.
2. Cover, from scope.md: **every** acceptance criterion, the happy path(s) traced end-to-end, the
   boundary conditions, and the error / failure scenarios the scope calls out.
3. One behaviour per test, arrange–act–assert, with a comment naming the scope requirement /
   acceptance criterion it encodes and why it matters.
4. Drive the feature through its **real public API** so each test is a genuine specification of
   behaviour — not of internal details.

#### Stay red, stay scoped
- Tests only — **no production code**, and do not touch the skeleton's placeholder bodies.
- Do not write unit tests here (the next workflow does that), and do not modify or break existing
  tests.
- The new tests must **compile** and **fail** when run — failing because the behaviour is
  unimplemented, not because they don't build. (`khazad-dum` verifies: tests build, the new tests
  fail, existing tests still pass.)

Finish by writing your status report (status report template) to
`.khazad-dum/orchestration_log/<feature>/2.1.2-red-e2e-{N}.md`.
