## Workflow 1.1.1 — Research Gate (Clarify the Plan)

You are a fresh agent at the **Research** step. This is a **looping clarification gate**: each cycle
you interrogate the human's research plan, append a fresh round of clarifying questions to the running
pre-review questionnaire, and report how well you understand the plan. You do **not** produce the
literature review here. You never see prior cycles' reasoning — only the current **Project Description**
and the questionnaire already in `process/`.

## Inputs (read-only)
- The provided **Project Description** (the human-owned `input/` plan) — it stays unchanged across
  cycles; the human answers in the questionnaire, not by editing it.
- `documentation/01_research/process/pre-literature-review-questionnaire.md` if it exists — read every
  prior round and the human's answers so you don't repeat questions and can judge what's now resolved.

## Do this
1. **Round number.** `N` = (number of existing `## Round` sections in the questionnaire) + 1.
   (If the CLI gave you a cycle number, use that.)
2. **Attack the plan — find problems, don't confirm understanding.** Hunt for: ambiguities & undefined
   terms; missing scope boundaries (what is explicitly OUT?), success criteria, constraints, intended
   use/audience; unstated assumptions; contradictions; feasibility risks given the only downstream
   experiment resources — **AWS EC2 instances + a home-lab server**. Be specific; a plan that "seems
   fine" hasn't been pushed hard enough.
3. **Score understanding.** Give an honest **0–100% certainty** that you understand the scope well
   enough to write a genuinely useful literature review without guessing, plus a one-line
   **recommendation**: *clarify further* or *ready to draft*. (The human makes the final call.)
4. **Append a round.** Using the **Template**, append a `## Round {N}` block to the pre-review
   questionnaire (never edit prior rounds) — start it with your certainty % and recommendation, then
   3–12 questions drawn from step 2. Prefer hard questions that demand written, researched answers.

Stop after writing. The human answers in-file (leaving `input/` unchanged) and decides whether to
re-run this gate or advance to the literature review.
