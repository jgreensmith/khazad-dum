# Step 01 — Research (Claude)

First Phase-1 step. Turns the human's research plan into a **literature review**, a **refined plan**
(iteration 1) and **experiment recommendations** that feed the Experiment phase.

## Pattern
**Two hybrid gates + complete.** Each gate loops: a fresh agent (never sees prior reasoning — only the
current `input/` plan and the questionnaires in `process/`) appends a round of questions and reports a
% certainty + recommendation; **the human makes the advance call** (hybrid, not a hard self-score
threshold). The three deliverables are drafted in `process/` and refined across the second gate, then
promoted to `output/` only on completion.

## Sub-prompts
- **1.1.1 `research-gate`** (pre-review, loops): critically analyse the `input/` plan (actively hunt
  ambiguities/gaps/risks). **Appends** a `## Round {N}` block to the single
  `process/pre-literature-review-questionnaire.md` — certainty % + recommendation, then 3–12 hard
  questions. Never writes the review. Human answers in-file, refines `input/`, advances when ready.
- **1.1.2 `draft-and-refine`** (post-review, loops): create-or-refine **three artifacts in `process/`** —
  `literature-review.md` (3–4 pp; inline `[..](URL)` + `*Certainty*` + `*Reliability*` tags with
  🟩/🟨/🟧/🟥 bands; `#sources` fallback when no URL), `refined-project-plan.md`,
  `experiment-recommendations.md`. Then **appends** a round to the single
  `process/post-literature-review-questionnaire.md`, including an **Additional research requested**
  section the human fills to send the next cycle back for more research.
- **1.1.3 `complete-research-step`**: final QC, then promote the three artifacts `process/ → output/`.
  Questionnaires stay in `process/`.

Recommendations are constrained to the only downstream resources: **AWS EC2 (`t3.micro`) + a home-lab
server**.

## In → out
- **In:** `input/` research plan.
- **Out:** `output/{literature-review,refined-project-plan,experiment-recommendations}.md`; the two
  appended questionnaires remain in `process/`.

## Flow
`input → research-gate → pre-questionnaire → human edits input / re-runs gate → (advance) →
draft-and-refine → 3 artifacts in process/ + post-questionnaire → human answers / requests more research
/ re-runs → (advance) → complete → promote to output/`.

## Key files
`workflows/01_research/prompts/{research-gate,draft-and-refine,complete-research-step}.md`;
templates `templates/{questionnaire,literature-review,project-description}.md`.
Shared Phase-1 rules: `workflows/research-planning-phase.md`.

> **Loop control is still deferred CLI work.** The prompts are authored loop-aware (append to one
> questionnaire, create-or-refine, human-advanced), but the current linear runner walks the three
> sub-prompts once each. True per-gate looping + human-gated advance is part of the interactive-CLI
> redesign — see [../roadmap.md](../roadmap.md).
