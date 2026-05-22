## Workflow 2.1.6 — Green Phase

The tests are certified and failing. Implement the **production code** that makes **all** tests pass.
The tests are the specification — satisfy them; do **not** change them.

## Inputs (read-only context)
- The provided **scope.md** — the feature's intent and constraints.
- The certified e2e and unit tests — your exact target.
- The skeleton from the Design phase — replace its placeholder bodies with real logic.
- If failing-test output from an earlier attempt is provided, start from what it reveals.

## Requirements

#### Make the tests pass
1. Implement the minimum correct logic to satisfy the failing tests — replace every `todo!()` /
   `unimplemented!()` body this feature needs with a real implementation.
2. Do **not** modify, add, weaken, or delete any test, and do not change the public signatures the
   tests rely on. If a test appears impossible to satisfy, implement everything else correctly and
   leave that failure standing — do **not** "fix" it by editing the test. `khazad-dum` handles the
   exhausted case (it routes to diagnosis); a silently altered test would defeat the whole pipeline.
3. Implement only what the tests and scope require — no untested features, no gold-plating.

#### Quality bar
- Idiomatic, readable Rust; comment only non-obvious logic.
- Add `///` doc comments to new public items.
- The result must clear the project's full gate — all tests passing, plus `cargo clippy` (no
  warnings) and `cargo fmt` — which `khazad-dum` runs to decide the outcome. You may run these
  yourself to check your work.

Finish by writing your status report (status report template) to
`.khazad-dum/orchestration_log/<feature>/2.1.6-green-{N}.md`. Summarise what you implemented; if any
tests remain failing, list them and what blocked you — this feeds the Green Diagnosis phase if the
escalation ladder is exhausted.
