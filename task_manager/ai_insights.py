"""Requests AI-generated insights from a local Ollama model."""
from datetime import date

import requests

from .models import Task
from .prioritizer import priority_score, sort_by_priority

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"
TIMEOUT_SECONDS = 120


class AIUnavailableError(Exception):
    """Raised when the local AI model can't be reached or fails."""


def build_prompt(tasks: list[Task], today: date | None = None) -> str:
    """Turn the task list into instructions for the AI model."""
    today = today or date.today()
    open_tasks = [t for t in sort_by_priority(tasks, today) if not t.completed]

    if open_tasks:
        lines = []
        for t in open_tasks:
            line = (f"- {t.title} | due {t.due_date.isoformat()} | "
                    f"importance {t.importance}/5 | ~{t.estimated_hours:g} hr | "
                    f"priority {priority_score(t, today):.0f}/100")
            if t.description:
                line += f" | notes: {t.description}"
            lines.append(line)
        task_text = "\n".join(lines)
    else:
        task_text = "(no open tasks)"

    return (
        f"You are a productivity coach. Today is {today:%A, %B %d, %Y}.\n"
        "Here are the user's open tasks, sorted by priority score "
        "(higher = more urgent):\n\n"
        f"{task_text}\n\n"
        "Give 3 to 5 short, specific recommendations to help the user get "
        "through this workload. Refer to tasks by name. Suggest what to do "
        "first, what to break up or reschedule, and how to spread the work "
        "over the coming days. Use a numbered list. Keep it under 200 words."
    )


def is_ollama_running() -> bool:
    """Quick check whether Ollama is reachable."""
    try:
        requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return True
    except requests.RequestException:
        return False


def get_ai_insights(tasks: list[Task], today: date | None = None) -> str:
    """Ask the local model for advice. Raises AIUnavailableError on failure."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": build_prompt(tasks, today),
                  "stream": False},
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        text = response.json().get("response", "").strip()
    except requests.Timeout as e:
        raise AIUnavailableError(
            "The AI model took too long to respond. Try again.") from e
    except requests.ConnectionError as e:
        raise AIUnavailableError(
            "Ollama isn't running. Install it from ollama.com, "
            "start it, and try again.") from e
    except requests.HTTPError as e:
        raise AIUnavailableError(
            f"Ollama returned an error. Make sure the model is installed:\n"
            f"ollama pull {MODEL}") from e
    except ValueError as e:  # response wasn't valid JSON
        raise AIUnavailableError("Got an unreadable response from Ollama.") from e

    if not text:
        raise AIUnavailableError("The AI model returned an empty response.")
    return text