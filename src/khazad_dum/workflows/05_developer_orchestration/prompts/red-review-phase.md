## Workflow 2.1.4 — Red Review Phase

Both test suites are written and failing. Before any production code exists, **certify that the tests
actually specify the feature** described in scope.md. You **review only** — write no code and change
no tests. Your output is a certainty score and a precise deficiency list that `khazad-dum` routes on.

## Inputs (read-only context)
- The provided **scope.md** — the source of truth for what the feature must do.
- The e2e tests (`e2e_tests` crate) and the unit tests (`#[cfg(test)]` modules) just written.

## Requirements

#### Critically review the tests against the scope (do this hard)
Actively hunt for ways the tests fail to specify the feature. For the **end-to-end requirements**
especially, check:
1. **Completeness** — is every acceptance criterion and end-to-end behaviour in scope.md covered by
   at least one test? Find what is missing.
2. **Correctness** — does each test assert the behaviour scope.md actually describes, not a
   misreading of it? Find assertions that are wrong or that contradict the scope.
3. **Boundaries & errors** — are the boundary conditions and error / failure paths from scope.md
   genuinely exercised, or only the happy path?
4. **Faithfulness** — do the tests pin behaviour through the real public API, or do they assert
   trivialities / internal details that a wrong implementation could still satisfy?

#### Score and report
- Self-assess **certainty (0–100)**: your confidence that making these tests pass will produce the
  feature scope.md describes.
- Record **every** deficiency concretely — which test, what kind, which scope requirement, and what
  it should assert instead — so the Red Edit phase can act without re-deriving your analysis. No
  deficiencies means the suite fully specifies the feature.

Write your routing report (review report template) to
`.khazad-dum/orchestration_log/<feature>/2.1.4-red-review-{N}.md`. `khazad-dum` advances to the Green
phase when your certainty clears its threshold, or routes to the Red Edit phase with your
deficiencies when it does not.
