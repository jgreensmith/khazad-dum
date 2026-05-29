# {{Feature / Slice Name}} — Scope

<!-- The exact end-to-end requirements for this vertical slice: the unit of work for one
     branch in the build phase. Keep it self-contained — a developer (human or agent) on
     this branch should be able to build and verify the slice from this file alone. -->

## Summary
<!-- One paragraph: what this slice delivers and the value it provides. -->


## End-to-End Behaviour
<!-- The slice traced through every layer it touches. Drop rows for untouched layers. -->

| Layer | What this slice adds / changes |
|-------|--------------------------------|
| Presentation / Interface | {{...}} |
| Application | {{...}} |
| Domain | {{...}} |
| Infrastructure | {{...}} |

## Acceptance Criteria
<!-- Testable and unambiguous. The slice is done when all are met. -->
- [ ] {{criterion}}

## Contracts & Data
<!-- Interfaces, types, schemas, and events this slice produces or consumes. -->


## Dependencies
<!-- Other slices/branches that must land first, and any shared modules (conflict risk). -->


## Existing Code & Refactoring
<!-- This slice's relationship to code that already exists. For a greenfield slice on a fresh
     skeleton, set the relationship to "new-only" and the rest to "None". The build phase reads
     this to decide whether a behaviour-preserving Enabling Refactor runs before the feature. -->

- **Relationship to existing code:** {{new-only | extends-existing | requires-enabling-refactor}}
- **Existing types / modules touched:** {{each existing item this slice builds on, and what it adds —
  e.g. new method `pay()` on `Order`, new variant on `Event`. "None" for new-only.}}
- **Enabling refactor required (before the feature):** {{the behaviour-preserving restructuring the
  existing code needs so this slice fits cleanly — e.g. "extract trait `Store` from `Db`", "split
  `handle()`". "None — purely additive" if not needed. This authorises and bounds what the build
  phase may reshape.}}
- **Changes existing behaviour?** {{no | yes}} — if **yes**, this slice is **human-led**: the
  automated build only performs behaviour-preserving refactoring, so changing what existing code
  *does* is out of its scope. Prefer to slice so any behaviour change is isolated and flagged here.


## Out of Scope
<!-- Explicitly what this slice does NOT cover. -->
