# Experiment Analysis — Report

khazad-dum runs you (the `report` stage of `build → start → fetch → graph → report`) after the graphs
have been generated. Write the **experiment report** that interprets the WAN-communication results
against the plan. Your output is a single file — this is not interactive.

## Inputs
- The graphs and statistics under `documentation/02_experiment/output/graphs/` (PNGs + `stats.json`).
- The raw results under `documentation/02_experiment/process/results/` (see the **Fetched result
  files** list appended below).
- The **Project Description** (appended below) — the plan, its open questions, and success criteria.
- The provided **report template** (appended below) — follow its structure.

## What to do
Write `documentation/02_experiment/output/experiment-report.md` following the template. It must:
- State what was measured and on what topology (remote AWS app ⇄ local homelab container, over the
  Twingate WAN tunnel).
- Embed the generated graphs with relative Markdown image links (e.g. `![](graphs/latency-cdf.png)`)
  and cite the figures from `stats.json` in the prose.
- Interpret the numbers **against the plan's success criteria / open questions**: what the experiment
  demonstrated about communicating over the WAN, what was decided, and what remains open.
- Be honest about limitations (sample size, single region, variance, failed runs).

## Rules
- Ground every claim in the fetched data / `stats.json`; do not invent results.
- Reference figures by their real filenames in `output/graphs/`. Do not embed images that do not exist.
