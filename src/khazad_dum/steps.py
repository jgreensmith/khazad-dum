from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Step:
    index: int
    slug: str
    name: str
    sub_prompts: tuple[str, ...] = ()

    @property
    def dir_name(self) -> str:
        return f"{self.index:02d}_{self.slug}"

    @property
    def scope_template_path(self) -> str:
        if self.sub_prompts:
            return f"{self.dir_name}/templates/project-description.md"
        return f"{self.dir_name}/templates/template.md"


STEPS: list[Step] = [
    Step(1, "research", "Research", sub_prompts=(
        "research-gate",
        "draft-and-refine",
        "complete-research-step",
    )),
    Step(2, "experiment", "Experiment", sub_prompts=(
        "experiment-decision",
        "complete-experiment-step",
    )),
    Step(3, "architecture", "Architecture"),
    Step(4, "project_management", "Project Management"),
    Step(5, "developer_orchestration", "Developer Orchestration"),
    Step(6, "delivery_and_maintenance", "Delivery and Maintenance"),
]


def get_step(identifier: str | int) -> Step | None:
    if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
        idx = int(identifier)
        for s in STEPS:
            if s.index == idx:
                return s
        return None
    for s in STEPS:
        if s.slug == identifier or s.dir_name == identifier:
            return s
    return None
