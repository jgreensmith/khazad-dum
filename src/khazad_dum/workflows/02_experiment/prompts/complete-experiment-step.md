## Workflow 1.2.2 — Complete Experiment Step

You run **after** the experiment has been provisioned (`khazad-dum build experiment`), run
(`start`), collected (`fetch`), and analysed (`graph` → `report`), and the human has refined the plan
in `input/` in light of the results. Using the current `input/` plus the generated experiment report,
produce the finalised handoff artifact for the Architecture phase: a **finalised project plan
(iteration 3)**.

Your only output is the file below.

## Inputs (read-only)
- The provided **Project Description** — the human's current, refined experiment plan in `input/`.
- The generated **experiment report** at `$CWD/documentation/02_experiment/output/experiment-report.md`
  and the graphs under `$CWD/documentation/02_experiment/output/graphs/`.
- The raw fetched results under `$CWD/documentation/02_experiment/process/results/` and any
  questionnaires under `process/`, for context on what was tested.

## Output — Finalised Project Plan (iteration 3)
Save as `$CWD/documentation/02_experiment/output/finalised-project-plan.md`.
- Synthesise the input plan with **what the experiment actually demonstrated** about WAN communication
  — what the measured latency/throughput/behaviour means for the project, what worked, what did not.
- Resolve the decisions the experiment was meant to settle; fold the outcomes back into the goal,
  scope (explicit IN and OUT), success criteria, and constraints.
- This is **iteration 3**: it is the direct input to the Architecture phase, so it must describe the
  application concretely enough for domain modelling and high-level technical architecture to begin.
- Call out any decisions still open that the Architecture phase must resolve.
