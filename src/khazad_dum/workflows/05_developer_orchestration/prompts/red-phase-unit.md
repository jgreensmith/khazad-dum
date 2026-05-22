## Workflow 2.1.3 — Red Phase: Unit Tests

The end-to-end tests are in place. Now write the **unit tests** that specify the behaviour of the
feature's individual components, co-located with the code they test. Write **no production code**.

## Inputs (read-only context)
- The provided **scope.md** — its **Contracts & Data** and per-layer behaviour define what each
  component must do.
- The skeleton (real signatures) and the e2e tests already written. Unit tests should **complement**
  the e2e tests, drilling into component-level logic, validation, and edge cases the e2e tests treat
  as a black box.

## Requirements

#### Write the unit tests
1. Place unit tests in `#[cfg(test)]` modules in the same file as the code under test.
2. For each new component (type / function / validator), cover its happy path, its boundary
   conditions, and its error / invalid-input paths.
3. One behaviour per test, arrange–act–assert; name each for the behaviour and expected outcome, and
   comment what it validates and why.
4. Keep tests isolated and order-independent; stub or fixture external dependencies at the unit
   boundary (this is what the Design phase's trait boundaries are for).

#### Stay red, stay scoped
- Tests only — **no production code**, do not touch placeholder bodies, and do not modify or break
  existing tests or the e2e tests.
- The new unit tests must **compile** and **fail** for want of implementation. (`khazad-dum`
  verifies: tests build, the new tests fail, existing tests still pass.)

Finish by writing your status report (status report template) to
`.khazad-dum/orchestration_log/<feature>/2.1.3-red-unit-{N}.md`.
