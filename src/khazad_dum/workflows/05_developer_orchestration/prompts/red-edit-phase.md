## Workflow 2.1.5 — Red Edit Phase

The Red Review phase found the tests do not yet faithfully specify the feature. **Fix the tests** to
resolve its deficiencies — and only those. Still **no production code**.

## Inputs (read-only context)
- The latest **review report** in `.khazad-dum/orchestration_log/<feature>/` (the highest-numbered
  `2.1.4-red-review-*.md`) — its `deficiencies` list is your worklist.
- The provided **scope.md** — the source of truth each fix must align the tests to.
- The existing e2e and unit tests.

## Requirements

#### Resolve every reported deficiency
1. For each entry in the review's `deficiencies` list, edit, add, or remove tests so the suite
   matches the scope requirement it names — add the missing coverage, correct the wrong assertion,
   exercise the missing boundary / error path.
2. Change tests **only to address the reported deficiencies**. Do not rewrite unrelated tests, and
   never weaken or delete a test merely to make a future implementation easier.

#### Stay red, stay scoped
- Tests only — **no production code**, do not touch placeholder bodies.
- After your edits the tests must still **compile** and **fail** for want of implementation, and
  existing tests must still pass. (`khazad-dum` verifies, then re-runs the Red Review phase to
  re-certify.)

Finish by writing your status report (status report template) to
`.khazad-dum/orchestration_log/<feature>/2.1.5-red-edit-{N}.md` — note which deficiencies you
resolved and how.
