<!-- Green Diagnosis report — written by Workflow 2.1.7 (Green Diagnosis Phase), which runs only
     when the Green Phase has exhausted khazad-dum's escalation ladder without passing the tests.
     Path: .khazad-dum/orchestration_log/<feature>/2.1.7-green-diagnosis-{N}.md

     The fenced ```json block is what khazad-dum routes on:
       "test-defect"  -> Red Edit Phase (bounded: one round-trip back, then a human takes over)
       "scope-defect" -> human refines scope.md
       "impl-hard"    -> human takes over the implementation
     Choose exactly one verdict. Keep the JSON valid. Delete this comment. -->

```json
{
  "workflow": "2.1.7",
  "feature": "<feature-slug>",
  "attempt": 1,
  "verdict": "test-defect | scope-defect | impl-hard",
  "offending_tests": ["test name or e2e_tests/file.rs"],
  "rationale": "one-line justification for the verdict"
}
```

## Diagnosis
<!-- The evidence. For test-defect: why the failing test(s) are wrong/impossible, citing the
     assertion and the scope requirement. For scope-defect: the ambiguity/contradiction in
     scope.md. For impl-hard: why test and scope are both sound and the work is simply hard.
     Explain why this verdict holds rather than the alternatives. -->
