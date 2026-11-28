"""Generates rule-based productivity recommendations."""
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

from .models import Task
from .prioritizer import priority_score, sort_by_priority

DAILY_HOURS_LIMIT = 6   # more than this due in one day = heavy day
BIG_TASK_HOURS = 4      # tasks this long should be broken down
LOOKAHEAD_DAYS = 7      # how far ahead to check for heavy days


@dataclass
class Recommendation:
    kind: str      # "focus", "warning", "tip", or "info"
    title: str
    message: str


def _names(tasks: list[Task], limit: int = 3) -> str:
    """Format task titles like: 'A', 'B', 'C', and 2 more"""
    names = [f"'{t.title}'" for t in tasks[:limit]]
    extra = len(tasks) - limit
    if extra > 0:
        names.append(f"and {extra} more")
    return ", ".join(names)


def generate_recommendations(tasks: list[Task],
                             today: date | None = None) -> list[Recommendation]:
    today = today or date.today()

    if not tasks:
        return [Recommendation("info", "Get started",
                               "Add your first task to get recommendations.")]

    open_tasks = sort_by_priority([t for t in tasks if not t.completed], today)
    if not open_tasks:
        return [Recommendation("info", "All caught up",
                               "Every task is complete. Nice work!")]

    recs = []

    # 1. What to do next
    top = open_tasks[0]
    recs.append(Recommendation(
        "focus", "Focus next",
        f"Start with '{top.title}' "
        f"(priority {priority_score(top, today):.0f}/100)."))

    # 2. Overdue tasks
    overdue = [t for t in open_tasks if t.due_date < today]
    if overdue:
        recs.append(Recommendation(
            "warning", f"{len(overdue)} overdue",
            f"Past due: {_names(overdue)}. "
            "Finish these or set new due dates."))

    # 3. Days with too much work due
    hours_by_day = defaultdict(float)
    for t in open_tasks:
        if today <= t.due_date < today + timedelta(days=LOOKAHEAD_DAYS):
            hours_by_day[t.due_date] += t.estimated_hours
    for day, hours in sorted(hours_by_day.items()):
        if hours > DAILY_HOURS_LIMIT:
            when = "today" if day == today else f"on {day:%A, %b %d}"
            recs.append(Recommendation(
                "warning", "Heavy day ahead",
                f"{hours:g} hours of work are due {when}. "
                "Start some of it earlier."))

    # 4. Large tasks
    big = [t for t in open_tasks if t.estimated_hours >= BIG_TASK_HOURS]
    if big:
        recs.append(Recommendation(
            "tip", "Break it down",
            f"{_names(big)} {'is' if len(big) == 1 else 'are'} "
            f"{BIG_TASK_HOURS}+ hours. Split into steps you can "
            "finish in one sitting."))

    # 5. Quick wins (skip the top task, it's already the focus)
    quick = [t for t in open_tasks[1:] if t.estimated_hours <= 1]
    if quick:
        recs.append(Recommendation(
            "tip", "Quick wins",
            f"{_names(quick)} take an hour or less. "
            "Knock them out between bigger tasks."))

    # 6. Workload summary
    total = sum(t.estimated_hours for t in open_tasks)
    plural = "s" if len(open_tasks) != 1 else ""
    recs.append(Recommendation(
        "info", "Workload",
        f"{len(open_tasks)} open task{plural}, about {total:g} hours total."))

    return recs