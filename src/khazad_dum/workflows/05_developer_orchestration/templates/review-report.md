<!-- Red Review report — written by Workflow 2.1.4 (Red Review Phase).
     Path: .khazad-dum/orchestration_log/<feature>/2.1.4-red-review-{N}.md

     The fenced ```json block is what khazad-dum routes on:
       certainty >= threshold  -> advance to the Green Phase (2.1.6)
       certainty <  threshold  -> go to the Red Edit Phase (2.1.5) with the deficiencies below
     Keep the JSON valid. "certainty" is 0-100. List a "deficiencies" entry for every gap; an
     empty list means the tests fully and correctly specify the feature. Delete this comment. -->

```json
{
  "workflow": "2.1.4",
  "feature": "<feature-slug>",
  "attempt": 1,
  "certainty": 0,
  "deficiencies": [
    {
      "test": "test name or e2e_tests/file.rs",
      "kind": "missing | incorrect | incomplete | contradicts-scope",
      "requirement": "the scope.md acceptance criterion / behaviour this concerns",
      "detail": "what is wrong and what the test should assert instead"
    }
  ]
}
```

## Assessment
<!-- Justify the certainty score: how completely and correctly the tests — the end-to-end tests
     especially — capture the end-to-end requirements in scope.md. Be concrete and reference
     specific tests and scope requirements. -->
