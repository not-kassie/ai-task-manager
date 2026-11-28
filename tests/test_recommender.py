from datetime import date, timedelta

from task_manager.models import Task
from task_manager.recommender import generate_recommendations

TODAY = date(2026, 11, 27)


def make(**overrides):
    fields = dict(title="Task", due_date=TODAY + timedelta(days=3),
                  importance=3, estimated_hours=2)
    fields.update(overrides)
    return Task(**fields)


def titles(recs):
    return [r.title for r in recs]


def test_no_tasks_suggests_getting_started():
    assert titles(generate_recommendations([], TODAY)) == ["Get started"]


def test_all_complete():
    recs = generate_recommendations([make(completed=True)], TODAY)
    assert titles(recs) == ["All caught up"]


def test_focus_is_highest_priority_task():
    urgent = make(title="Urgent", due_date=TODAY, importance=5)
    later = make(title="Later", due_date=TODAY + timedelta(days=10))
    recs = generate_recommendations([later, urgent], TODAY)
    assert recs[0].title == "Focus next"
    assert "Urgent" in recs[0].message


def test_overdue_detected():
    recs = generate_recommendations(
        [make(due_date=TODAY - timedelta(days=2))], TODAY)
    assert any("overdue" in r.title for r in recs)


def test_heavy_day_detected():
    tomorrow = TODAY + timedelta(days=1)
    tasks = [make(title="A", due_date=tomorrow, estimated_hours=4),
             make(title="B", due_date=tomorrow, estimated_hours=4)]
    assert "Heavy day ahead" in titles(generate_recommendations(tasks, TODAY))


def test_big_task_flagged():
    recs = generate_recommendations([make(estimated_hours=6)], TODAY)
    assert "Break it down" in titles(recs)