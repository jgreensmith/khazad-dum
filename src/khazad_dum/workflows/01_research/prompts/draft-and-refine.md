## Workflow 1.1.2 — Literature Review & Post-Review Gate

The pre-review gate has passed. You now build and iteratively refine **three artifacts in `process/`**,
and run a second clarification gate. Each cycle: create-or-refine the artifacts, then append a round of
questions to the running post-review questionnaire. You never see prior cycles' reasoning — only the
current files on disk. **Do not write to `output/` here** — that is the complete step's job.

## Inputs
- The provided **Project Description** (current `input/` plan).
- `process/pre-literature-review-questionnaire.md` (what was clarified before drafting).
- `process/post-literature-review-questionnaire.md` if it exists — read prior rounds, the human's
  answers, and especially the **Additional research requested** section.
- The three artifacts below if they already exist — **refine them in place; don't restart**.

## Downstream resource constraint (hard)
Every experiment recommendation must run on **AWS EC2 instances** (default `t3.micro`) **+ a home-lab
server**. Flag anything outside this set as out-of-scope, with the trade-off.

## Each cycle — create or refine these three in `documentation/01_research/process/`
1. **`literature-review.md`** — 3–4 pp, using the **Template**. Purpose: feed the experiment/
   architecture phases (not academic publication); weight it toward what is testable on the resources
   above. **Every factual or conceptual claim** carries an inline source link and two tags:
   - Link: `[Author, Year|brief_source](URL_or_DOI)`.
   - `*Certainty*:⬛ XX%` — your confidence the claim is correct / your reading of the source is accurate.
   - `*Reliability*:⬛ XX%` — how trustworthy the source itself is (research paper / official docs >
     book > blog/forum).
   - Bands for the ⬛: 🟩 95–100 · 🟨 87–94 · 🟧 77–86 · 🟥 <76.
   - No locatable URL? Link to `(literature-review#sources)` and list the source under **Sources**.
   - Honour the post-questionnaire's **Additional research requested** — expand the review to cover it.
2. **`refined-project-plan.md`** (iteration 1) — synthesise the input plan with what the review
   established: tighten goal, scope (explicit IN and OUT), success criteria, constraints; and list the
   **decisions left open for the experiment to resolve**.
3. **`experiment-recommendations.md`** — for each recommendation state: what to test, which gap/open
   decision it resolves, and how it maps to EC2 vs. home-lab. Concrete enough to become server
   configs/scripts.

## Then — append a post-review round
Using the questionnaire **Template**, append a `## Round {N}` block (N = existing rounds + 1) to
`process/post-literature-review-questionnaire.md`: start with a one-line note on what you changed this
cycle plus your confidence the three artifacts are ready to hand off, then 4–12 questions to sharpen the
refined plan and experiment recommendations, plus the **Additional research requested** section for the
human to fill.

Stop after writing. The human answers, refines `input/`, and decides whether to re-run this step or
advance to complete.
