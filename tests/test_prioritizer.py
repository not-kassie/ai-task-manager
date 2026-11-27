from datetime import date, timedelta

from task_manager.models import Task
from task_manager.prioritizer import (
    priority_label, priority_score, sort_by_priority,
)

TODAY = date(2026, 11, 27)


def make(**overrides):
    fields = dict(title="Task", due_date=TODAY, importance=3, estimated_hours=2)
    fields.update(overrides)
    return Task(**fields)


def test_overdue_important_quick_task_scores_max():
    task = make(due_date=TODAY - timedelta(days=1), importance=5, estimated_hours=1)
    assert priority_score(task, TODAY) == 100


def test_far_away_unimportant_long_task_scores_zero():
    task = make(due_date=TODAY + timedelta(days=30), importance=1, estimated_hours=5)
    assert priority_score(task, TODAY) == 0


def test_completed_task_scores_zero():
    assert priority_score(make(completed=True), TODAY) == 0


def test_sooner_due_date_scores_higher():
    soon = make(due_date=TODAY + timedelta(days=1))
    later = make(due_date=TODAY + timedelta(days=10))
    assert priority_score(soon, TODAY) > priority_score(later, TODAY)


def test_sort_puts_highest_first_and_completed_last():
    low = make(title="low", due_date=TODAY + timedelta(days=20), importance=1)
    high = make(title="high", importance=5)
    done = make(title="done", importance=5, completed=True)
    ordered = sort_by_priority([low, done, high], TODAY)
    assert [t.title for t in ordered] == ["high", "low", "done"]


def test_priority_labels():
    assert priority_label(85) == "High"
    assert priority_label(50) == "Medium"
    assert priority_label(10) == "Low"