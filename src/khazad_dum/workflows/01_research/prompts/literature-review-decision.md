## Literature Review / Decision Workflow

## Objectives
- Self-assess understanding of the project description
- EITHER:
	- Append more clarifying questions to the questionnaire and end the workflow.
	- Complete a literature review based on the **template**

## Requirements
### Step 1 — Read & Comprehend
Read the provided **Project Description and Questionnaire** in full. Identify any ambiguities, undefined terms, or missing context. 

### Step 2 — Self-Assess Comprehension Certainty
After reading, perform an honest internal assessment. Ask yourself:

- Can I precisely restate the project goal in one sentence?
- Do I understand the domain well enough to identify relevant literature?
- Are the scope boundaries (what is IN and OUT of scope) unambiguous?
- Do I understand the intended use or audience of the literature review?
- Are there undefined acronyms, named frameworks, or proprietary terms?
- Are there any other ambiguities, undefined terms, or missing context?

Assign yourself a **percentage certainty** for how confident you are that you fully understand the scope of the project, and the requirements of the literature review. 

### Step 3 — Branch on Certainty Score

#### IF certainty < 98:
- Do NOT attempt the literature review.
- Instead, append additional questions to `$CWD/documentation/01_research/process/pre-literature-review-questionnaire.md` to help clarify the scope of the project, and the requirements of the literature review. 
-  Before appending questions - add the **percentage certainty** obtained in Step 2.

#### IF certainty >= 98:
Proceed immediately to carry out a literature review:
- The literature review should be 3 - 4 pages, it is not for academic use, it is purely to obtain valuable information to be drawn upon during **later** architecture/design phases of this project.
- Use the template provided to format.
- Save the file as `$CWD/documentation/01_research/output/literature-review.md`
- **Formatting rules applied in this document:**
	- Every factual or conceptual claim carries an Obsidian-style citation: `[Author, Year|brief_source_name - e.g. cloudflare](URL_or_DOI)`.
	- Each citation is followed immediately by a **certainty and reliability tag**: '*Certainty*:⬛ *XX%*, *Reliability*: ⬛ *XX%*' :
		- where XX is a number between 1 - 100.
		- **Certainty** is the model's confidence that the cited source actually supports the claim as stated (0–100%)
		- **Reliability:** The models estimation of how reliable the cited source is.
	- Percentages: 🟩 95–100% · 🟨 87–94% · 🟧 77–86% · 🟥 <76%
	- Ideal sources include:
		- Research papers/ articles: `[Author, Year](URL)`
		- Company/ platform technical documentation: `e.g. [Microsoft Docs](URL)`
		- Books etc. 
	- Note: if you're using prior training and cannot find a URL to source, just use `[Author, Year](literature-review#References)` in text, and be sure to add `APA` style reference in the 'References' section

