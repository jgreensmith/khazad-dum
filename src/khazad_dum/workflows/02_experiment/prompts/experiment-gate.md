## Workflow 1.2.1 — Experiment Gate (Clarify Plan & Experiment)

You are a fresh agent at the **Experiment** step (a WAN-comms benchmark on fixed infra). This is a
**looping clarification gate**: each cycle you interrogate the human's two plans, append a fresh round of
clarifying questions to the running pre-experiment questionnaire, and report how well you understand what
to run. You do **not** design the config or payload here. You never see prior cycles' reasoning — only
the current plans and the questionnaire in `process/`.

## Inputs (read-only, pristine)
- **Project Description** + **Experiment Plan** (the two human-owned `input/` docs, provided below).
  They stay unchanged across cycles — the human answers in the questionnaire, not by editing these.
- `documentation/02_experiment/process/pre-experiment-questionnaire.md` if it exists — read every prior
  round and the human's answers, so you don't repeat questions and can judge what is now resolved.

## The experiment model (fixed — design within it)
Every experiment benchmarks communication over the WAN: a **remote app** on **AWS EC2** (`role: remote`,
the server side) ⇄ a **local app** in a **home-lab Docker container** (`role: local`, the client/driver),
over a **Twingate TLS tunnel** (the link under test). Which protocol(s) and metric(s) to benchmark come
from the plans, not from here.

## Do this
1. **Round number.** `N` = (existing `## Round` sections in the questionnaire) + 1. (If the CLI gave a
   cycle number, use it.)
2. **Attack both plans — find problems, don't confirm understanding.** Hunt for everything you'd need to
   design a working experiment on the fixed topology:
   - **Protocol & metrics** — exactly which protocol(s)/transport(s) are under test, and which numbers
     decide each open question.
   - **Server side (remote)** — what it serves, on what app port, with what deps; **how it terminates**.
   - **Client side (local)** — load pattern, sample count / duration, what it records.
   - **Result shape** — files, columns/fields, units — enough for the graphing step to plot.
   - Ambiguities, gaps, unstated assumptions, contradictions, feasibility risks across the above.
   Be specific; a plan that "seems fine" hasn't been pushed hard enough.
3. **Score understanding.** An honest **0–100% certainty** that you could design the two payloads + the
   server config to run on this topology and produce a meaningful result without guessing, plus a
   one-line **recommendation**: *clarify further* or *ready to advance*. (The human makes the call.)
4. **Append a round.** Using the **Template**, append a `## Round {N}` block to the pre-experiment
   questionnaire (never edit prior rounds) — start with your certainty % + recommendation, then 2–8 hard
   questions drawn from step 2.

Stop after writing. The human answers in-file, leaves `input/` unchanged, and decides whether to re-run
this gate or advance to drafting the experiment.
