# Feature Scopes — {{PROJECT}}

<!-- Ordered vertical slices of the layered architecture, narrowest first. Each slice is
     one feature delivered end-to-end and becomes an actionable branch in the build phase.
     - #            = build order (respect dependencies).
     - Scope doc    = path to the slice's exact end-to-end requirements.
     - Depends on   = ids of slices that must land first ("—" if none).
     - Parallel-safe = yes when the slice has no dependency AND no overlapping
                       files/modules with another in-flight slice (no conflict risk).
     - Certainty    = the agent's confidence it understands this slice's end-to-end
                       requirements; below 97% it must be queried in the questionnaire. -->

| # | Slice (feature) | Branch | Scope doc | Depends on | Parallel-safe | Certainty |
|---|-----------------|--------|-----------|------------|---------------|-----------|
| 1 | {{slice name}} | feat/{{slug}} | documentation/features/{{feat-name}}/scope.md | {{— or ids}} | {{yes/no}} | {{0–100%}} |
