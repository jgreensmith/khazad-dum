# Workflow 1.2.2 - Create Experiment Config Decision

## Objectives
- Self-assess understanding of the Experiment Requirements
- EITHER:
	A - Append more clarifying questions to the questionnaire and end the workflow.
OR
	B - Configure the experiment scripts and terraform JSON config

## Requirements
### Step 1 — Read & Comprehend
Read the provided **Experiment Requirements**. Identify any ambiguities, undefined terms, or missing context. 

### Step 2 — Self-Assess Comprehension Certainty
After reading, perform an honest internal assessment. Assign yourself a **percentage certainty** for how confident you are that you fully understand the scope, purpose and requirements of the experiment. 

### Step 3 — Branch on Certainty Score

#### IF certainty < 98:
- Do NOT attempt to configure the experiment.
- Instead, append additional questions to `$CWD/documentation/02_experiment/process/pre-experiment-questionnaire.md` to help with further clarification. 
- Before appending questions - add the **percentage certainty** obtained in Step 2.

#### IF certainty >= 98:
- Configure the experiment:
	- Generate the required scripts and save to: `$CWD/documentation/02_experiment/process/scripts/`
	- Generate the JSON config and save this as `$CWD/documentation/02_experiment/process/experiment-config.json`

### ========= todo:  
- provide code snippet for JSON format
- context for khazad-dun experiment config