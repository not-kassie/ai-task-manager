from datetime import date

import pytest
import requests

from task_manager import ai_insights
from task_manager.ai_insights import (
    AIUnavailableError, build_prompt, get_ai_insights,
)
from task_manager.models import Task

TODAY = date(2026, 11, 27)
TASK = Task(title="Write README", due_date=date(2026, 11, 29),
            importance=4, estimated_hours=1)


class FakeResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


def test_prompt_includes_task_details():
    prompt = build_prompt([TASK], TODAY)
    assert "Write README" in prompt
    assert "2026-11-29" in prompt


def test_prompt_skips_completed_tasks():
    done = Task(title="Old task", due_date=TODAY, completed=True)
    assert "Old task" not in build_prompt([TASK, done], TODAY)


def test_returns_model_text(monkeypatch):
    monkeypatch.setattr(ai_insights.requests, "post",
                        lambda *a, **k: FakeResponse({"response": "1. Do it"}))
    assert get_ai_insights([TASK], TODAY) == "1. Do it"


def test_ollama_not_running_raises_friendly_error(monkeypatch):
    def refuse(*args, **kwargs):
        raise requests.ConnectionError()
    monkeypatch.setattr(ai_insights.requests, "post", refuse)
    with pytest.raises(AIUnavailableError, match="isn't running"):
        get_ai_insights([TASK], TODAY)


def test_empty_response_raises(monkeypatch):
    monkeypatch.setattr(ai_insights.requests, "post",
                        lambda *a, **k: FakeResponse({"response": ""}))
    with pytest.raises(AIUnavailableError):
        get_ai_insights([TASK], TODAY)