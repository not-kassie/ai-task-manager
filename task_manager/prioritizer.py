"""Calculates priority scores for tasks."""
from datetime import date

from .models import Task

URGENCY_WEIGHT = 0.5
IMPORTANCE_WEIGHT = 0.35
QUICK_WIN_WEIGHT = 0.15
URGENCY_WINDOW_DAYS = 14   # tasks due further out than this get no urgency
QUICK_WIN_HOURS = 1


def _urgency(task: Task, today: date) -> float:
    """0.0 (due far away) to 1.0 (due today or overdue)."""
    days_left = (task.due_date - today).days
    if days_left <= 0:
        return 1.0
    if days_left >= URGENCY_WINDOW_DAYS:
        return 0.0
    return 1 - days_left / URGENCY_WINDOW_DAYS


def priority_score(task: Task, today: date | None = None) -> float:
    """Return a 0-100 priority score. Completed tasks score 0."""
    if task.completed:
        return 0.0
    today = today or date.today()
    importance = (task.importance - 1) / 4          # 1-5 -> 0.0-1.0
    quick_win = 1.0 if task.estimated_hours <= QUICK_WIN_HOURS else 0.0
    score = (URGENCY_WEIGHT * _urgency(task, today)
             + IMPORTANCE_WEIGHT * importance
             + QUICK_WIN_WEIGHT * quick_win)
    return round(score * 100, 1)


def priority_label(score: float) -> str:
    """Convert a score into High / Medium / Low."""
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def sort_by_priority(tasks: list[Task], today: date | None = None) -> list[Task]:
    """Open tasks first (highest score first), completed tasks last."""
    today = today or date.today()
    return sorted(
        tasks,
        key=lambda t: (t.completed, -priority_score(t, today), t.due_date),
    )