## Workflow 1.1.1 — Research Gate (Literature Review or Clarify)

You are a fresh agent entering the **Research** step. This is a **looping gate**: each cycle you
either (a) decide the research plan is solid enough and produce a **literature review**, or
(b) decide it is not yet, and produce a **new questionnaire** of hard clarifying questions for
the human to answer. The human refines the plan between cycles; you never see the previous
cycle's reasoning — only the current `input/` and any questionnaires already in `process/`.

## Inputs (read-only)
- The provided **Project Description** (the human-owned research plan).
- Any existing questionnaires in `$CWD/documentation/01_research/process/` — read them to see
  what has already been asked and answered, and to determine the current cycle number.

## Step 1 — Determine the cycle
Count the questionnaire files already in `process/` matching
`pre-literature-review-questionnaire-*.md`. The current cycle `N` is that count **+ 1**.
(If the CLI has told you the cycle number, use that instead.)

## Step 2 — Critically analyse the plan (do this hard)
Your job is to **actively find problems**, not to confirm you understand. Interrogate the
Project Description and hunt for:
- **Ambiguities & undefined terms** — vague goals, undefined acronyms, proprietary/framework
  names with no definition.
- **Gaps** — missing scope boundaries (what is explicitly OUT of scope?), missing success
  criteria, missing constraints, unspecified intended use/audience.
- **Unstated assumptions** — things the plan takes for granted that may not hold.
- **Contradictions & tensions** — goals that conflict, or that conflict with the stated
  constraints/resources.
- **Risks & feasibility concerns** — parts of the plan that look technically shaky, unproven,
  or likely to fail given the available experiment resources (AWS EC2 instances + a home lab
  server — see Step 4).
Be sceptical and specific. A plan that "seems fine" usually has not been pushed hard enough.

## Step 3 — Self-assess certainty
Give yourself an honest **percentage certainty (0–100%)** that you fully understand the project
scope and could write a genuinely useful literature review without guessing. Ask: can I restate
the project goal in one sentence? Are scope boundaries unambiguous? Do I know the domain well
enough to find relevant literature? Have the problems found in Step 2 been resolved by the
current input?

## Step 4 — Branch on certainty

### IF certainty < 98%  →  produce a new questionnaire (do NOT write a literature review)
- Write a **new** file (do not append to or edit any existing questionnaire):
  `$CWD/documentation/01_research/process/pre-literature-review-questionnaire-{N}.md`
- Use the provided **questionnaire template**.
- At the very top, record the **cycle number** and your **% certainty** from Step 3.
- Turn the problems found in Step 2 into 3–12 clarifying questions. Prefer challenging
  questions that force the human to do real thinking and give **written** answers; other
  question types are allowed where they fit the template.
- Stop here. The human will refine the plan and re-run this gate.

### IF certainty ≥ 98%  →  produce the literature review
- Write `$CWD/documentation/01_research/output/literature-review.md` using the provided
  **literature review template**.
- 3–4 pages. Not for academic publication — its purpose is to feed the later
  experiment/architecture phases with useful, reliable information.
- Remember the only experiment resources available downstream are **AWS EC2 instances and a
  home lab server**; weight the review toward what is testable on those.
- **Citation rules (apply to every factual/conceptual claim):**
  - Obsidian-style citation: `[Author, Year|brief_source_name - e.g. cloudflare](URL_or_DOI)`.
  - Immediately followed by a certainty & reliability tag:
    `*Certainty*:⬛ *XX%*, *Reliability*:⬛ *XX%*` (XX = 1–100).
    - **Certainty** = your confidence the source actually supports the claim as stated.
    - **Reliability** = your estimate of how trustworthy the source is.
  - Bands: 🟩 95–100% · 🟨 87–94% · 🟧 77–86% · 🟥 <76%.
  - Preferred sources: research papers/articles, official platform/technical docs, books.
  - If relying on prior training with no locatable URL, cite
    `[Author, Year](literature-review#References)` in text and add a full **APA** entry under
    References.
