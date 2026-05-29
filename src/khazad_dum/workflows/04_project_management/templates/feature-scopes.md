# Feature Scopes — {{PROJECT}}

<!-- Ordered vertical slices of the layered architecture, narrowest first. Each slice is
     one feature delivered end-to-end and becomes an actionable branch in the build phase.
     - #            = build order (respect dependencies).
     - Scope doc    = path to the slice's exact end-to-end requirements.
     - Depends on   = ids of slices that must land first ("—" if none).
     - Parallel-safe = yes when the slice has no dependency AND no overlapping
                       files/modules with another in-flight slice (no conflict risk).
     - Existing code = new (new code only), extends (adds methods/variants to existing
                       types), or refactor (needs a behaviour-preserving enabling refactor
                       of existing code before the feature). See the slice's scope doc.
     - Certainty    = the agent's confidence it understands this slice's end-to-end
                       requirements and its impact on existing code; below 97% it must be
                       queried in the questionnaire. -->

| # | Slice (feature) | Branch | Scope doc | Depends on | Parallel-safe | Existing code | Certainty |
|---|-----------------|--------|-----------|------------|---------------|---------------|-----------|
| 1 | {{slice name}} | feat/{{slug}} | documentation/features/{{feat-name}}/scope.md | {{— or ids}} | {{yes/no}} | {{new/extends/refactor}} | {{0–100%}} |
