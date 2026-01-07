"""Обработчики виджетов пользовательского пространства."""
from PySide6.QtCore import Signal

from client.src.src.handlers.widgets_view_handlers.base import BaseViewHandler
from client.src.gui.widgets_view.userflow_view import TaskWidgetView


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


if __name__ == '__main__':
    pass
