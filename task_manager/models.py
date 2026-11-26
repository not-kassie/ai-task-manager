from dataclasses import dataclass, field, asdict
from datetime import date, datetime
import uuid


@dataclass
class Task:
    title: str
    due_date: date
    importance: int = 3
    estimated_hours: float = 1.0
    description: str = ""
    completed: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    "sets up the task object and validates the input values"
    def __post_init__(self):
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("Title is required.")
        if not 1 <= self.importance <= 5:
            raise ValueError("Importance must be between 1 and 5.")
        if self.estimated_hours <= 0:
            raise ValueError("Estimated hours must be greater than 0.")

    def to_dict(self) -> dict:
        d = asdict(self)
        d["due_date"] = self.due_date.isoformat()
        d["created_at"] = self.created_at.isoformat()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Task":
        d = d.copy()
        d["due_date"] = date.fromisoformat(d["due_date"])
        d["created_at"] = datetime.fromisoformat(d["created_at"])
        return cls(**d)