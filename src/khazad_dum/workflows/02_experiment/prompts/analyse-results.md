# Experiment Analysis — Graphs

khazad-dum runs you (the `graph` stage of `build → start → fetch → graph → report`) after the
experiment results have been fetched back to the laptop. Turn the **raw result data** into clear
**graphs** and a small machine-readable **statistics summary**. Your outputs are files only — this is
not interactive.

## Inputs
- The raw results fetched from each endpoint, under `documentation/02_experiment/process/results/<endpoint-name>/`
  (see the **Fetched result files** list appended below for the exact paths). These are the
  machine-readable outputs (CSV/JSON) the experiment payload wrote — typically per-sample latency,
  throughput, timestamps, and possibly server-side logs.
- The **Project Description** + **Experiment Plan** (appended below) for the metrics and success
  criteria that matter.

## What to do
1. **Inspect** the fetched files to learn their actual structure before plotting — do not assume
   columns or units; read them.
2. Using a popular Python data/stats stack — **pandas + matplotlib** — load the data and produce
   graphs that answer the experiment's question about WAN communication. Good defaults: a latency
   distribution (histogram/CDF), latency over time, and throughput where available. Add others if the
   data warrants.
3. Save every graph as a PNG into `documentation/02_experiment/output/graphs/`, with descriptive
   filenames (e.g. `latency-cdf.png`).
4. Write `documentation/02_experiment/output/graphs/stats.json` with the key summary statistics
   (e.g. count, mean, median, p50/p90/p95/p99 latency, throughput) — the report stage and the human
   read this.

## How to run Python
You have a shell. Create an isolated environment so you don't pollute the system, e.g.:
```bash
python3 -m venv documentation/02_experiment/process/.venv
documentation/02_experiment/process/.venv/bin/pip install --quiet pandas matplotlib
documentation/02_experiment/process/.venv/bin/python <<'PY'
# load process/results/**, plot, save PNGs + stats.json under output/graphs/
PY
```

## Rules
- **Only plot data that is actually present.** Never fabricate or interpolate missing measurements;
  if a file is empty or a run failed, note it in `stats.json` rather than inventing numbers.
- Use `matplotlib` non-interactively (`matplotlib.use("Agg")`); never call `plt.show()`.
- Keep going if one endpoint's data is missing — graph what you have.
