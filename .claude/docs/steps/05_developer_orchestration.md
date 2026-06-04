# Step 05 — Developer Orchestration (Claude)

**Phase 2 (Active Build).** A deterministic **TDD state machine** that builds one feature at a time
from its `documentation/features/<feat>/scope.md` (authored by PM). Not a questionnaire/loop phase.
Global rules: `workflows/active-build-phase.md`.

## Core split (what makes it deterministic)
Agents write **code + one status report**; **khazad-dum is the deterministic part** — after each agent
run it executes the project's `test_commands` (`.khazad-dum/config.json`) as the *real* gate, **owns
all git**, and drives every transition + escalation. The agent's self-reported "tests pass" is never
trusted. scope.md is the agent's **complete context** — no codebase trawling beyond the modules it names.

## Nine phases (`prompts/*-phase.md`, titled `Workflow 2.1.x`, tier-agnostic — never name a model/effort)
Listed in **execution** order (numbering is a stable id, so order isn't numeric):
1. **2.1.8 `enabling-refactor`** — *optional, first, only if scope's Existing Code & Refactoring asks.*
   Behaviour-preserving reshape so the feature fits. No tests, no feature code. Own "tidy-first" commit.
2. **2.1.1 `design`** — skeleton (modules/types/sigs, `todo!()` bodies). May add new types or
   methods/variants on existing types; never changes existing behaviour/sigs. Gate: `cargo build`.
3. **2.1.2 `red-e2e`** — e2e/integration tests in the `e2e_tests` crate from scope's acceptance criteria.
4. **2.1.3 `red-unit`** — co-located `#[cfg(test)]` unit tests. (red gate: tests build + new tests FAIL
   + existing pass.)
5. **2.1.4 `red-review`** — review-only; scores **certainty** the tests capture scope + lists
   deficiencies (`review-report`). Gate: certainty ≥ threshold → green; else → red-edit.
6. **2.1.5 `red-edit`** — fixes only the flagged tests, stays red → back to 2.1.4 (bounded loop).
7. **2.1.6 `green`** — production code to pass ALL tests; never edits tests. Gate: all pass + clippy + fmt.
8. **2.1.9 `cleanup-refactor`** — *after green.* TDD third beat: tidy this feature's code,
   behaviour-preservingly. No-op valid. Gate: prior green set unchanged + clippy + fmt.
9. **2.1.7 `green-diagnosis`** — only when green exhausts the ladder; emits a **verdict**
   `test-defect | scope-defect | impl-hard` (`diagnosis-report`).

**Pipeline:** [enabling-refactor?] → design → red-e2e → red-unit → [red-review ↔ red-edit] → green →
[cleanup-refactor] → (on green exhaustion) diagnosis.

## Rules khazad-dum enforces (config, not prompts)
- **Refactoring is behaviour-preserving only.** A slice that must *change* behaviour is routed to a
  human, so the red gate's "existing tests still pass" invariant holds.
- **Refactor failure asymmetry:** enabling-refactor fail → escalate → **human (blocks)**;
  cleanup-refactor fail → escalate → on exhaustion **revert to the green commit and proceed** (polish
  must not sink a passing feature).
- **Escalation ladder:** retry at tier up to a budget, then climb `haiku/medium → sonnet/medium →
  opus/high → human`. khazad-dum sets `--model`/`--effort`.
- **Green-blocked routing:** top-tier green fail → diagnosis → `test-defect` kicks back to red-edit
  **once** (else human); `scope-defect`/`impl-hard` → human.
- **Git = khazad-dum only.** Checkout branch, commit at each passed gate, push/PR. Agents never run git.

## Reports (templates → `.khazad-dum/orchestration_log/<feature>/<workflow-id>-<slug>-{N}.md`)
`status-report` (all phases incl. both refactors), `review-report` (2.1.4), `diagnosis-report` (2.1.7).
Each = a machine-readable ```json block (the routing signal) + prose audit.

## Key files
`workflows/05_developer_orchestration/prompts/{enabling-refactor,design,red-phase-e2e,red-phase-unit,red-review,red-edit,green,cleanup-refactor,green-diagnosis}-phase.md`;
templates `templates/{status-report,review-report,diagnosis-report}.md`; `workflows/active-build-phase.md`.
