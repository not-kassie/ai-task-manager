"""Handles saving and loading tasks from a JSON file."""
import json
import os
import sys
from pathlib import Path

from .models import Task

APP_NAME = "AITaskManager"


def get_data_dir() -> Path:
    """Return the per-user folder where app data is stored."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"
    data_dir = base / APP_NAME
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


class TaskStorage:
    def __init__(self, path: Path | None = None):
        self.path = path or get_data_dir() / "tasks.json"

    def load(self) -> list[Task]:
        if not self.path.exists():
            return []
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
            return [Task.from_dict(t) for t in data]
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            # Corrupted file: keep a backup and start fresh instead of crashing
            self.path.replace(self.path.with_suffix(".bak"))
            return []

    def save(self, tasks: list[Task]) -> None:
        # Write to a temp file first so a crash mid-save can't corrupt the data
        tmp = self.path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in tasks], f, indent=2)
        tmp.replace(self.path)