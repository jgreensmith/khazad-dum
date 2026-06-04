# Step 01 — Research (Claude)

First Phase-1 step. Turns the human's research plan into a **literature review**, then a
**refined plan + experiment recommendations** that feed the Experiment phase. Iteration 1 → research output.

## Pattern
Gate + complete (certainty loop). A fresh agent each cycle; it never sees prior reasoning — only the
current `input/` plan and the questionnaires already in `process/`.

## Sub-prompts
- **1.1.1 `literature-review-decision`** (gate, loops): critically analyse the `input/` plan (actively
  hunt ambiguities/gaps/risks) → self-assess % certainty. **<98%** → write a NEW
  `process/pre-literature-review-questionnaire-{N}.md` and stop. **≥98%** → write
  `output/literature-review.md` (3–4 pp; Obsidian-style citations + 🟩/🟨/🟧/🟥 certainty+reliability tags).
- **1.1.2 `complete-research-step`**: runs after the human refines `input/` in light of the review →
  writes `output/refined-project-plan.md` + `output/experiment-recommendations.md`. Recommendations are
  constrained to the only downstream resources: **AWS EC2 + a home lab server**.

## In → out
- **In:** `input/` research plan (iter 1).
- **Out:** `output/literature-review.md`, `output/refined-project-plan.md`,
  `output/experiment-recommendations.md`; numbered questionnaires in `process/`.

## Flow
`input → analyse → certain?` — no → questionnaire → `process/` → human edits `input/` → re-run.
Yes → `literature-review` → `output/` → (human refines `input/`) → complete → refined-plan + experiment-recs.

## Key files
`workflows/01_research/prompts/{literature-review-decision,complete-research-step}.md`;
templates `templates/{questionnaire,literature-review,project-description}.md`.
Shared Phase-1 rules: `workflows/research-planning-phase.md`.
