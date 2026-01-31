"""Обработчики виджетов пользовательского пространства."""
from PySide6.QtCore import Signal

import datetime

from client.src.src.handlers.widgets_view_handlers.base import BaseViewHandler
from client.src.gui.widgets_view.userflow_view import TaskWidgetView, NotesWidgetView, ScheduleWidgetView, ReminderWidgetView
from client.src.base import DataStructConst


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


class ReminderViewHandler(BaseViewHandler):

    reminder_completed = Signal(str)  # Вызывается при закрытии напоминания. Возвращает название напоминания
    reminder_added = Signal(str)  # Вызывается при добавлении напоминания. Возвращает название напоминания
    reminder_edited = Signal(str, str)  # Вызывается при редактировании напоминания. Первая строка - старое название, вторая - новое

    def __init__(self, view: ReminderWidgetView, max_reminder_length: int = DataStructConst.max_reminder_length):
        super().__init__(view)
        self._view = view
        self._view.set_max_reminder_length(max_reminder_length)
        self._view.reminder_added.connect(lambda name: self._on_remainder_added(name))
        self._view.reminder_completed.connect(lambda name: self._on_reminder_completed(name))
        self._view.reminder_edited.connect(lambda last_name, current_name: self._on_reminder_edited(last_name, current_name))

    def _on_remainder_added(self, label: str):
        self.reminder_added.emit(label)

    def _on_reminder_completed(self, label: str):
        self.reminder_completed.emit(label)

    def _on_reminder_edited(self, last_name: str, current_name: str):
        self.reminder_edited.emit(last_name, current_name)

    def set_reminders(self, labels: tuple[str, ...] | list[str]):
        self._view.set_reminders(labels)

    def add_reminder(self, label: str):
        self._view.add_reminder(label)
        self.reminder_added.emit(label)

    def delete_reminder(self, label: str):
        self._view.delete_reminder(label)
        self.reminder_completed.emit(label)

    def set_max_reminder_length(self, length: int):
        self._view.set_max_reminder_length(length)

    def max_reminder_length(self) -> int:
        return self._view.max_reminder_length()


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
