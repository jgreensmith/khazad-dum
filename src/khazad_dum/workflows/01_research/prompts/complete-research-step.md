## Workflow 1.1.2 — Complete Research Step

You run **after** the literature review is done and the human has refined the research plan in
`input/` in light of it. Using the current `input/` plus the research outputs, produce two
finalised handoff artifacts for the next phases: a **refined project plan** and **experiment
recommendations**.

Your only outputs are the two files below.

## Inputs (read-only)
- The provided **Project Description** (the human's current, refined research plan).
- `$CWD/documentation/01_research/output/literature-review.md`.
- Any questionnaires under `$CWD/documentation/01_research/process/` for additional context on
  what was clarified.

## Available experiment resources (hard constraint)
The only resources available for any downstream experiment are:
- **AWS EC2 instances** (provisioned by khazad-dum; default `t3.micro`).
- **A home lab server.**
Every experiment recommendation must be achievable with these. Do not recommend managed
services, GPUs, or infrastructure outside this set unless you explicitly flag it as
out-of-scope and explain the trade-off.

## Output 1 — Refined Project Plan
Save as `$CWD/documentation/01_research/output/refined-project-plan.md`.
- Synthesise the input plan with what the literature review established.
- Tighten the goal, scope (explicit IN and OUT), success criteria, and constraints.
- Call out **what decisions remain open** and are expected to be resolved by the experiment.

## Output 2 — Experiment Recommendations
Save as `$CWD/documentation/01_research/output/experiment-recommendations.md`.
- Base recommendations on the **gaps and open questions** surfaced by the literature review.
- For each recommendation, state: what to test, why (which gap/decision it resolves), and how
  it maps onto the available resources (EC2 vs. home lab).
- Be concrete enough that the Experiment phase can turn these into server configs and scripts.
