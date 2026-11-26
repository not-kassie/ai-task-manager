
from datetime import date

import pytest

from task_manager.manager import TaskManager
from task_manager.models import Task
from task_manager.storage import TaskStorage


def make_manager(tmp_path):
    return TaskManager(TaskStorage(tmp_path / "tasks.json"))


def sample_task(**overrides):
    fields = dict(title="Write README", due_date=date(2026, 11, 29))
    fields.update(overrides)
    return Task(**fields)


def test_add_task_persists(tmp_path):
    make_manager(tmp_path).add(sample_task())
    reloaded = make_manager(tmp_path)
    assert len(reloaded.tasks) == 1
    assert reloaded.tasks[0].title == "Write README"


def test_update_task(tmp_path):
    m = make_manager(tmp_path)
    task = m.add(sample_task())
    m.update(task.id, title="Write full README", importance=5)
    updated = make_manager(tmp_path).get(task.id)
    assert updated.title == "Write full README"
    assert updated.importance == 5


def test_delete_task(tmp_path):
    m = make_manager(tmp_path)
    task = m.add(sample_task())
    m.delete(task.id)
    assert make_manager(tmp_path).tasks == []


def test_toggle_complete(tmp_path):
    m = make_manager(tmp_path)
    task = m.add(sample_task())
    assert m.toggle_complete(task.id).completed is True
    assert m.toggle_complete(task.id).completed is False


def test_empty_title_rejected():
    with pytest.raises(ValueError):
        sample_task(title="   ")


def test_importance_out_of_range_rejected():
    with pytest.raises(ValueError):
        sample_task(importance=6)


def test_corrupted_file_does_not_crash(tmp_path):
    (tmp_path / "tasks.json").write_text("not valid json")
    assert make_manager(tmp_path).tasks == []