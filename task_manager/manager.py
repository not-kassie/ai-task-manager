"""Create, update, delete, and complete tasks."""
from dataclasses import replace

from .models import Task
from .storage import TaskStorage


class TaskManager:
    def __init__(self, storage: TaskStorage):
        self.storage = storage
        self.tasks: list[Task] = storage.load()

    def _index(self, task_id: str) -> int:
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                return i
        raise KeyError(f"No task with id {task_id}")

    def _save(self) -> None:
        self.storage.save(self.tasks)

    def get(self, task_id: str) -> Task:
        return self.tasks[self._index(task_id)]

    def add(self, task: Task) -> Task:
        self.tasks.append(task)
        self._save()
        return task

    def update(self, task_id: str, **changes) -> Task:
        i = self._index(task_id)
        # replace() builds a new Task, so validation runs again
        self.tasks[i] = replace(self.tasks[i], **changes)
        self._save()
        return self.tasks[i]

    def delete(self, task_id: str) -> None:
        del self.tasks[self._index(task_id)]
        self._save()

    def toggle_complete(self, task_id: str) -> Task:
        task = self.get(task_id)
        return self.update(task_id, completed=not task.completed)