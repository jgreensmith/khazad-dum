## Workflow 2.1.7 — Green Diagnosis Phase

You run only because the Green phase exhausted every implementation attempt `khazad-dum` was willing
to make and the tests still fail. Your job is **not** to write code or edit tests — it is to
**diagnose why**, so `khazad-dum` can route correctly. Choose exactly one verdict and back it with
evidence.

## Inputs (read-only context)
- The provided **scope.md** — the source of truth for intended behaviour.
- The still-failing tests, and the **green status report(s)** in the orchestration log (including the
  failing-test output and what blocked the implementation).
- The production code the Green phase produced.

## Requirements

#### Determine the cause and choose a verdict
Examine the still-failing test(s) against the scope and the implementation, then classify the blocker
as exactly one of:
- **`test-defect`** — the implementation is reasonable but a test is wrong or impossible: it asserts
  behaviour scope.md does not call for, contradicts another test, or cannot be satisfied by any valid
  implementation. `khazad-dum` sends the pipeline back to the Red Edit phase to correct the test.
  This back-step is allowed **once**; if Green still fails after it, a human takes over.
- **`scope-defect`** — the tests faithfully encode scope.md, but scope.md itself is ambiguous or
  contradictory, so no correct implementation can exist. `khazad-dum` escalates to a human to refine
  the scope.
- **`impl-hard`** — tests and scope are both sound; the work is simply beyond what the automated
  attempts achieved. `khazad-dum` escalates to a human to take over the implementation.

#### Report the verdict with evidence
- Name the offending test(s), cite the specific failing assertion(s) and the relevant scope.md
  requirement(s), and explain in a sentence or two why this verdict holds rather than the
  alternatives. Be decisive — `khazad-dum` acts on the verdict directly.

Write your diagnosis report (diagnosis report template) to
`.khazad-dum/orchestration_log/<feature>/2.1.7-green-diagnosis-{N}.md`.
