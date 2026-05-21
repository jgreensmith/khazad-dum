from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Step:
    index: int
    slug: str
    name: str

    @property
    def dir_name(self) -> str:
        return f"{self.index:02d}_{self.slug}"

    @property
    def prompt_file(self) -> str:
        return f"{self.dir_name}.md"


STEPS: list[Step] = [
    Step(1, "research", "Research"),
    Step(2, "experiment", "Experiment"),
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
