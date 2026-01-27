"""Обработчики виджетов пользовательского пространства."""
from PySide6.QtCore import Signal

import datetime

from client.src.src.handlers.widgets_view_handlers.base import BaseViewHandler
from client.src.gui.widgets_view.userflow_view import TaskWidgetView, NotesWidgetView, ScheduleWidgetView


class TaskViewHandler(BaseViewHandler):
    """
    Обработчик виджета задач в ПП.

    :param window: обрабатываемое окно.
    :param tasks: словарь с задачами вида {<name>: <id>}. Нужен для установления уникальности между именем задачи и её id.
    """

    task_completed = Signal(str)

    def __init__(self, window: TaskWidgetView, tasks: dict = None):
        super().__init__(window)
        self._tasks = tasks
        self._completed_tasks = []

        self._window = window
        self._window.task_completed.connect(self._on_task_completed)
        for task in tasks:
            window.add_task(task)

    def _on_task_completed(self, task: str):
        self._tasks.pop(task)
        self._completed_tasks.append(task)

    @property
    def tasks(self):
        return self._tasks

    @tasks.setter
    def tasks(self, tasks: tuple[str, ...]):
        self._tasks = tasks
        self._completed_tasks = []

    @property
    def completed_tasks(self) -> list:
        return self._completed_tasks


class NotesViewHandler(BaseViewHandler):

    def __init__(self, view: NotesWidgetView):
        super().__init__(view)
        self._view = view

    def set_notes(self, text: str):
        """Устанавливает текст в заметку."""
        self._view.set_notes(text)

    def notes(self) -> str:
         return self._view.notes()


class ScheduleViewHandler(BaseViewHandler):

    def __init__(self, view: ScheduleWidgetView):
        super().__init__(view)
        self._view = view

    def add_event(self, name: str, time_start: datetime.time, time_end: datetime.time):
        pass

    def delete_event(self):
        pass


if __name__ == '__main__':
    pass
