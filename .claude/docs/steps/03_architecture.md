# Step 03 — Architecture (Claude)

Third Phase-1 step. Produces the domain model + high-level technical architecture and **scaffolds the
real project skeleton**. Iteration 3 → architecture output (iter 4). Stack default = **Rust / cargo workspace**.

## Pattern
Loop + complete — **breaks the gate mould: no certainty branch.** Every cycle does BOTH (a) refine the
design artifacts and (b) emit a fresh questionnaire. Nothing auto-advances; the **human advances via
the CLI** when satisfied.

## Sub-prompts
- **1.3.1 `domain-modelling-loop`** (loops): each cycle drills four fronts — ubiquitous language,
  high-level technical architecture, DDD building blocks, and the **architectural-layers table** (the
  grid PM slices vertically) — and writes/refines in `process/`: `c4-diagram.md` (Mermaid
  `C4Context`+`C4Container`), `ddd-table.md` (incl. the layers table), `skeleton-proposal.md` (cargo
  layout + proposed test commands), plus a new `domain-modelling-questionnaire-{N}.md`.
- **1.3.2 `complete-architecture-step`** (human-triggered): finalise `output/c4-diagram.md` +
  `output/ddd-table.md` + `output/detailed-project-description.md` (iter 4); **scaffold the skeleton in
  `$CWD` root** (cargo workspace, structure only — `todo!()`/stub bodies, test scaffolding, no logic);
  write `test_commands` into `.khazad-dum/config.json` (merge, don't clobber).

## In → out
- **In:** `input/` finalised plan (iter 3) from Experiment.
- **Out:** `output/{c4-diagram.md,ddd-table.md,detailed-project-description.md}`; a scaffolded cargo
  workspace in `$CWD` root; `test_commands` in `.khazad-dum/config.json`. Working artifacts in `process/`.

## Flow
loop cycle → (questionnaire + C4 + DDD + skeleton-proposal in `process/`) → human edits `input/` →
re-run … → human advances → complete → finalised C4/DDD/description + scaffolded skeleton + test_commands.

## Key files
`workflows/03_architecture/prompts/{domain-modelling-loop,complete-architecture-step}.md`;
templates `templates/{c4-diagram,ddd-table,skeleton-proposal,detailed-project-description,questionnaire,project-description}.md`.
Shared Phase-1 rules: `workflows/research-planning-phase.md`.
