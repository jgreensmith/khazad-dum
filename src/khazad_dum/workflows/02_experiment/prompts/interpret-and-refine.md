## Workflow 1.2.3 — Interpret Results & Refine Plan

The experiment has run (`build → start → fetch → graph → report`). Each cycle: synthesise what it
demonstrated into a **finalised project plan** in `process/`, and append a round of questions challenging
that reading, until the human is satisfied. You never see prior cycles' reasoning — only the current
files. **Do not write to `output/`** — that is the complete step's job.

## Inputs (read-only)
- **Project Description** + **Experiment Plan** (pristine `input/` docs, below) and the refined
  `process/project-description.md` (iteration 2) + `process/experiment-plan.md`.
- `documentation/02_experiment/output/experiment-report.md` + `output/graphs/` (PNGs + `stats.json`).
- `documentation/02_experiment/process/results/` — the raw fetched data.
- `process/post-experiment-questionnaire.md` if it exists — read prior rounds + the human's answers.

## Each cycle
1. **Create-or-refine** `process/finalised-project-plan.md` (**iteration 3**): synthesise the plan with
   **what the experiment actually demonstrated** about WAN communication — measured
   latency/throughput/behaviour, what worked, what didn't. Resolve the decisions the experiment was meant
   to settle; fold the outcomes into goal, scope (IN/OUT), success criteria, constraints. This is the
   direct input to Architecture, so describe the application concretely enough for domain modelling to
   begin. Flag any decision still open for Architecture.
2. **Append a post-experiment round.** Using the **Template**, append a `## Round {N}` block to
   `process/post-experiment-questionnaire.md` (never edit prior rounds): start with your confidence the
   finalised plan is ready to hand off, then 3–10 questions challenging what the results mean for the
   project (interpretation, generalisability, risks the numbers expose).

Stop after writing. The human answers in-file (leaving `input/` unchanged) and decides whether to re-run
this step or advance to complete.
