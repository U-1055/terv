"""
Представления виджетов пользовательского пространства.
"""

from PySide6.QtCore import Signal

from client.src.gui.widgets_view.base_view import BaseView
from client.src.ui.ui_userflow_task_widget import Ui_Form as UserFlowTaskWidget
from client.src.ui.ui_userflow_notes_window import Ui_Form as UserFlowNotesWidget
from client.src.gui.sub_widgets.widgets import UserFlowTask


class TaskWidgetView(BaseView):
    task_completed = Signal(str)

    def __init__(self):
        super().__init__()
        self._view = UserFlowTaskWidget()
        self._view.setupUi(self)

    def complete_task(self, name: str):
        self.task_completed.emit()

    def add_task(self, name):
        widget = UserFlowTask(name)
        self._view.verticalLayout_2.addWidget(widget)

    def to_loading_state(self):
        pass

    def to_normal_state(self):
        pass

    @property
    def tasks(self) -> tuple[str, ...]:
        return '', ''


class NotesWidgetView(BaseView):

    def __init__(self):
        super().__init__()
        self._view = UserFlowNotesWidget()
        self._view.setupUi(self)

    def set_notes(self, text: str):
        self._view.textEdit.setText(text)

    def notes(self) -> str:
        return self._view.textEdit.toPlainText()


class ScheduleWidgetView(BaseView):

    def __init__(self):
        super().__init__()


if __name__ == '__main__':
    pass
