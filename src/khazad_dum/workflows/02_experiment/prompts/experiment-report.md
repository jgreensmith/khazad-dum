# Experiment Analysis — Report

khazad-dum runs you (the `report` stage of `build → start → fetch → graph → report`) after the graphs are
generated. Write the **experiment report** interpreting the WAN-comms results against the plan. Your
output is a single file — this is not interactive.

## Inputs
- The graphs + statistics under `documentation/02_experiment/output/graphs/` (PNGs + `stats.json`).
- The raw results under `documentation/02_experiment/process/results/` (see the **Fetched result files**
  list appended below) — including each endpoint's `run.log`.
- The **payload script docs** at `documentation/02_experiment/process/payload/<name>/<name>.md`.
- The **Project Description** + **Experiment Plan** (appended below) — plan, open questions, success
  criteria.
- The provided **report Template** (appended below) — follow its structure.

## What to do
Write `documentation/02_experiment/output/experiment-report.md` from the template. It must:
- State what was measured and on what topology (remote AWS app ⇄ local home-lab container, over the
  Twingate WAN tunnel).
- **Fill the `## Architecture` mermaid diagram** with the topology actually run: both endpoints, the
  Twingate link under test, the protocol + app port, and where results were recorded.
- Embed the generated graphs with relative links (e.g. `![](graphs/latency-cdf.png)`) and cite the
  numbers from `stats.json` in the prose.
- Interpret the numbers **against the plan's success criteria / open questions**: what was demonstrated,
  decided, and what remains open. Be honest about limitations (sample size, single region, variance,
  failed runs — check each `run.log`).
- **Append each payload's `<name>.md` as an appendix subsection**, so the report fully documents what ran.

## Rules
- Ground every claim in the fetched data / `stats.json`; do not invent results.
- Reference figures by their real filenames in `output/graphs/`; don't embed images that don't exist.
