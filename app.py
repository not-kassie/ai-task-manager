"""AI Task Manager desktop app."""
from datetime import date
from tkinter import messagebox

import customtkinter as ctk

from task_manager.manager import TaskManager
from task_manager.models import Task
from task_manager.storage import TaskStorage
from task_manager.prioritizer import priority_label, priority_score, sort_by_priority
from task_manager.recommender import generate_recommendations

RED = "#d9534f"
PRIORITY_COLORS = {"High": RED, "Medium": "#e0a030", "Low": "#5cb85c", "Done": "gray"}
REC_COLORS = {"focus": "#3b8ed0", "warning": RED, "tip": "#5cb85c", "info": "gray"}


class TaskDialog(ctk.CTkToplevel):
    """Popup window for adding or editing a task."""

    def __init__(self, parent, on_save, task: Task | None = None):
        super().__init__(parent)
        self.on_save = on_save
        self.title("Edit Task" if task else "Add Task")
        self.geometry("420x500")
        self.resizable(False, False)
        self.transient(parent)
        # keep focus on this dialog
        self.after(100, self.grab_set)  

        pad = {"padx": 20, "pady": (10, 0), "anchor": "w"}

        ctk.CTkLabel(self, text="Title *").pack(**pad)
        self.title_entry = ctk.CTkEntry(self, width=380)
        self.title_entry.pack(padx=20)

        ctk.CTkLabel(self, text="Description").pack(**pad)
        self.desc_box = ctk.CTkTextbox(self, width=380, height=80)
        self.desc_box.pack(padx=20)

        ctk.CTkLabel(self, text="Due date (YYYY-MM-DD) *").pack(**pad)
        self.due_entry = ctk.CTkEntry(self, width=380)
        self.due_entry.pack(padx=20)

        ctk.CTkLabel(self, text="Importance (1 = low, 5 = high)").pack(**pad)
        self.importance = ctk.CTkSegmentedButton(
            self, values=["1", "2", "3", "4", "5"]
        )
        self.importance.pack(padx=20, anchor="w")

        ctk.CTkLabel(self, text="Estimated hours").pack(**pad)
        self.hours_entry = ctk.CTkEntry(self, width=380)
        self.hours_entry.pack(padx=20)

        self.error_label = ctk.CTkLabel(self, text="", text_color=RED)
        self.error_label.pack(padx=20, pady=(10, 0))

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(pady=15)
        ctk.CTkButton(buttons, text="Cancel", fg_color="gray",
                      command=self.destroy).pack(side="left", padx=5)
        ctk.CTkButton(buttons, text="Save",
                      command=self.save).pack(side="left", padx=5)

        if task:
            self.title_entry.insert(0, task.title)
            self.desc_box.insert("1.0", task.description)
            self.due_entry.insert(0, task.due_date.isoformat())
            self.importance.set(str(task.importance))
            self.hours_entry.insert(0, f"{task.estimated_hours:g}")
        else:
            self.due_entry.insert(0, date.today().isoformat())
            self.importance.set("3")
            self.hours_entry.insert(0, "1")

        self.title_entry.focus()

    def save(self):
        try:
            due = date.fromisoformat(self.due_entry.get().strip())
        except ValueError:
            self.error_label.configure(text="Due date must be YYYY-MM-DD.")
            return
        try:
            hours = float(self.hours_entry.get().strip())
        except ValueError:
            self.error_label.configure(text="Estimated hours must be a number.")
            return

        fields = {
            "title": self.title_entry.get(),
            "description": self.desc_box.get("1.0", "end").strip(),
            "due_date": due,
            "importance": int(self.importance.get()),
            "estimated_hours": hours,
        }
        try:
            self.on_save(fields)
        # validation errors from the Task model
        except ValueError as e: 
            self.error_label.configure(text=str(e))
            return
        self.destroy()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI Task Manager")
        self.geometry("1100x650")
        self.minsize(850, 500)

        self.manager = TaskManager(TaskStorage())

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(header, text="AI Task Manager",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        ctk.CTkButton(header, text="+ Add Task",
                      command=self.open_add_dialog).pack(side="right")

        # Body: task list on the left, recommendations on the right
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.list_frame = ctk.CTkScrollableFrame(
            body, label_text="Tasks (sorted by priority)")
        self.list_frame.pack(side="left", fill="both", expand=True)

        self.sidebar = ctk.CTkScrollableFrame(
            body, width=300, label_text="Recommendations")
        self.sidebar.pack(side="right", fill="y", padx=(10, 0))

        self.refresh()

    # ---------- display ----------
    def refresh(self):
        self._refresh_tasks()
        self._refresh_recommendations()

    def _refresh_tasks(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not self.manager.tasks:
            ctk.CTkLabel(self.list_frame,
                         text="No tasks yet. Click '+ Add Task' to get started.",
                         text_color="gray").pack(pady=40)
            return

        today = date.today()
        for task in sort_by_priority(self.manager.tasks, today):
            self._task_row(task, priority_score(task, today))

    def _refresh_recommendations(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        for rec in generate_recommendations(self.manager.tasks):
            color = REC_COLORS[rec.kind]
            card = ctk.CTkFrame(self.sidebar, border_width=2, border_color=color)
            card.pack(fill="x", pady=5)
            ctk.CTkLabel(card, text=rec.title, anchor="w", text_color=color,
                         font=ctk.CTkFont(size=14, weight="bold")
                         ).pack(fill="x", padx=10, pady=(8, 0))
            ctk.CTkLabel(card, text=rec.message, anchor="w", justify="left",
                         wraplength=250).pack(fill="x", padx=10, pady=(2, 8))

    def _task_row(self, task: Task, score: float):
        row = ctk.CTkFrame(self.list_frame)
        row.pack(fill="x", pady=4)

        checkbox = ctk.CTkCheckBox(
            row, text="", width=24,
            command=lambda t=task: self.toggle_complete(t.id))
        checkbox.pack(side="left", padx=(10, 5), pady=10)
        if task.completed:
            checkbox.select()

        # Priority badge
        label = "Done" if task.completed else priority_label(score)
        badge_text = label if task.completed else f"{label}\n{score:.0f}"
        ctk.CTkLabel(row, text=badge_text, width=64, corner_radius=6,
                     fg_color=PRIORITY_COLORS[label], text_color="white",
                     font=ctk.CTkFont(size=12, weight="bold")
                     ).pack(side="left", padx=5, pady=8)

        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, padx=5, pady=8)

        title_font = ctk.CTkFont(size=15, weight="bold",
                                 overstrike=task.completed)
        ctk.CTkLabel(info, text=task.title, anchor="w", font=title_font,
                     text_color="gray" if task.completed else None
                     ).pack(fill="x")

        overdue = not task.completed and task.due_date < date.today()
        details = (f"Due {task.due_date:%b %d, %Y}  •  "
                   f"Importance {task.importance}/5  •  "
                   f"{task.estimated_hours:g} hr")
        if overdue:
            details = "OVERDUE  •  " + details
        ctk.CTkLabel(info, text=details, anchor="w",
                     text_color=RED if overdue else "gray").pack(fill="x")

        ctk.CTkButton(row, text="Delete", width=70,
                      fg_color=RED, hover_color="#b52b27",
                      command=lambda t=task: self.delete_task(t)
                      ).pack(side="right", padx=(5, 10))
        ctk.CTkButton(row, text="Edit", width=70,
                      command=lambda t=task: self.open_edit_dialog(t)
                      ).pack(side="right", padx=5)

    # ---------- actions ----------
    def open_add_dialog(self):
        TaskDialog(self, on_save=self.add_task)

    def add_task(self, fields: dict):
        self.manager.add(Task(**fields))
        self.refresh()

    def open_edit_dialog(self, task: Task):
        TaskDialog(self, task=task,
                   on_save=lambda fields: self.edit_task(task.id, fields))

    def edit_task(self, task_id: str, fields: dict):
        self.manager.update(task_id, **fields)
        self.refresh()

    def toggle_complete(self, task_id: str):
        self.manager.toggle_complete(task_id)
        self.after(0, self.refresh)  # let the checkbox finish its click first

    def delete_task(self, task: Task):
        if messagebox.askyesno("Delete task", f"Delete '{task.title}'?"):
            self.manager.delete(task.id)
            self.refresh()


if __name__ == "__main__":
    ctk.set_appearance_mode("system")
    app = App()
    app.mainloop()