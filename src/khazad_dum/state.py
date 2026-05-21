from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path


STATE_DIR_NAME = ".khazad-dum"
STATE_FILE_NAME = "state.json"


@dataclass
class State:
    completed: list[str] = field(default_factory=list)
    current: str | None = None
    sub_completed: dict[str, list[str]] = field(default_factory=dict)

    @classmethod
    def load(cls, project_root: Path) -> "State":
        path = project_root / STATE_DIR_NAME / STATE_FILE_NAME
        if not path.exists():
            return cls()
        data = json.loads(path.read_text())
        return cls(
            completed=data.get("completed", []),
            current=data.get("current"),
            sub_completed=data.get("sub_completed", {}),
        )

    def save(self, project_root: Path) -> None:
        path = project_root / STATE_DIR_NAME / STATE_FILE_NAME
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2) + "\n")

    def mark_completed(self, step_dir: str) -> None:
        if step_dir not in self.completed:
            self.completed.append(step_dir)
        if self.current == step_dir:
            self.current = None

    def mark_sub_completed(self, step_dir: str, sub: str) -> None:
        subs = self.sub_completed.setdefault(step_dir, [])
        if sub not in subs:
            subs.append(sub)
