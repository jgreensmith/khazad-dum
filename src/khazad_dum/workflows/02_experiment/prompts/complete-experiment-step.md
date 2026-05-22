## Workflow 1.2.2 — Complete Experiment Step

You run **after** the experiment has been provisioned (`khazad-dum build experiment`), executed on
the servers, and the human has recorded the results and refined the plan in `input/` in light of
them. Using the current `input/` plus the experiment outputs, produce the finalised handoff artifact
for the Architecture phase: a **finalised project plan (iteration 3)**.

Your only output is the file below.

## Inputs (read-only)
- The provided **Project Description** — the human's current, refined experiment plan in `input/`.
- The **experiment results / report** the human recorded after running the experiment (look under
  `$CWD/documentation/02_experiment/input/` and `process/`).
- The promoted server config (`input/servers.json` + `input/scripts/`) and any questionnaires under
  `process/`, for context on what was tested.

## Output — Finalised Project Plan (iteration 3)
Save as `$CWD/documentation/02_experiment/output/finalised-project-plan.md`.
- Synthesise the input plan with **what the experiment actually demonstrated** — what worked, what
  did not, and what that means for the project.
- Resolve the decisions the experiment was meant to settle; fold the outcomes back into the goal,
  scope (explicit IN and OUT), success criteria, and constraints.
- This is **iteration 3**: it is the direct input to the Architecture phase, so it must describe the
  application concretely enough for domain modelling and high-level technical architecture to begin.
- Call out any decisions still open that the Architecture phase must resolve.
