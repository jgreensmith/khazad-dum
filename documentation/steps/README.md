# khazad-dum — per-step documentation

Human-facing guides to the six steps khazad-dum drives a project through. Each doc explains what the
step does, what you need to know to use it, and includes a **mermaid** control-flow diagram.

For the system itself (the orchestrator, prompt assembly, infrastructure) see the docs one level up:
[architecture.md](../architecture.md), [terraform.md](../terraform.md), [workflows.md](../workflows.md).

## The two phases

- **Phase 1 — Research & Planning (steps 1–4):** human-in-control planning. Each step works in
  `documentation/<step>/{input,process,output}/`; **`input/` is yours**, the agent never writes to
  it. You refine the plan between runs and advance when ready.
- **Phase 2 — Active Build (steps 5–6):** the agents build the real project on feature branches.
  khazad-dum owns git and the test gate.

## The steps

| # | Step | Pattern | Guide |
|---|------|---------|-------|
| 1 | Research | gate + complete (certainty loop) | [01_research.md](01_research.md) |
| 2 | Experiment | gate + complete + `build→start→fetch→graph→report` | [02_experiment.md](02_experiment.md) |
| 3 | Architecture | loop + complete; scaffolds the skeleton | [03_architecture.md](03_architecture.md) |
| 4 | Project Management | loop + complete; emits `scope.md` + branch plan | [04_project_management.md](04_project_management.md) |
| 5 | Developer Orchestration | deterministic 9-phase TDD pipeline | [05_developer_orchestration.md](05_developer_orchestration.md) |
| 6 | Delivery & Maintenance | single prompt — *not yet authored* | [06_delivery_and_maintenance.md](06_delivery_and_maintenance.md) |

## The plan, iteration by iteration

The project plan is refined across the phases; each step hands the next a more concrete iteration:

```
iter 1  research input
iter 2  research output  →  experiment input
iter 3  experiment output →  architecture input
iter 4  architecture output (detailed-project-description.md) → project-management input
iter 5  project-management output (finalised-project-plan.md) →  Active Build
```
