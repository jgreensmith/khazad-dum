<!-- Status report — written by every Developer Orchestration workflow at the end of its run,
     except Red Review (2.1.4) and Green Diagnosis (2.1.7), which use their own routing templates.
     Path: .khazad-dum/orchestration_log/<feature>/<workflow-id>-<slug>-{N}.md

     The fenced ```json block is the machine-readable part khazad-dum logs — keep it valid JSON.
     "outcome" is your own report of how the run went; it is advisory, because khazad-dum decides
     pass/fail by running the project's configured commands itself. The prose below is the human
     audit trail. Replace every placeholder; delete this comment. -->

```json
{
  "workflow": "2.1.x",
  "feature": "<feature-slug>",
  "attempt": 1,
  "outcome": "completed | blocked",
  "files_changed": ["path/to/file.rs"],
  "summary": "one-line summary of what this run produced",
  "blockers": []
}
```

## What I did
<!-- The work performed this run, and any decision a reviewer or the next workflow should know. -->

## Notes for the next workflow
<!-- Optional: context that will help whoever runs next. Omit if none. -->
