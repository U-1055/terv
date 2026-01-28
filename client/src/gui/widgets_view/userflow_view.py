"""
Представления виджетов пользовательского пространства.
"""
import typing as tp

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QVBoxLayout, QListWidget, QDialog, QHBoxLayout, QPushButton, QAbstractItemView, QLabel
from client.src.gui.widgets_view.base_view import BaseView
from client.src.ui.ui_userflow_task_widget import Ui_Form as UserFlowTaskWidget
from client.src.ui.ui_userflow_notes_widget import Ui_Form as UserFlowNotesWidget
from client.src.gui.sub_widgets.widgets import UserFlowTask
from client.src.base import GuiLabels, DataStructConst


MultiSelection = QAbstractItemView.SelectionMode.MultiSelection


class BaseUserFlowWidget(BaseView):
    """
    Базовый класс виджетов ПП.
    :param name: название виджета (из констант DataStructConst).
    """

    def __init__(self, name: str):
        super().__init__()
        self.name = name


class TaskWidgetView(BaseUserFlowWidget):
    task_completed = Signal(str)

    def __init__(self):
        super().__init__(DataStructConst.tasks_widget)
        self._view = UserFlowTaskWidget()
        self._view.setupUi(self)
        self._view.label.setText(GuiLabels.tasks_widget)

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


class NotesWidgetView(BaseUserFlowWidget):

    def __init__(self):
        super().__init__(DataStructConst.notes_widget)
        self._view = UserFlowNotesWidget()
        self._view.setupUi(self)
        self._view.label.setText(GuiLabels.notes_widget)

    def set_notes(self, text: str):
        self._view.textEdit.setText(text)

    def notes(self) -> str:
        return self._view.textEdit.toPlainText()


class MemoryWidgetView(BaseUserFlowWidget):

    def __init__(self):
        super().__init__(DataStructConst.memory_widget)


class ScheduleWidgetView(BaseView):

    def __init__(self):
        super().__init__()


class WidgetSettingsMenu(QDialog):
    """Виджет настроек ПП. Принимает список размещаемых виджетов."""
    set = Signal(tp.Any, tuple[str, ...])  # Вызывается при закрытии окна. Возвращает выбранные пользователем виджеты

    def __init__(self, widgets: list[str], selected_widgets: list[str]):
        super().__init__()
        self._main_layout = QVBoxLayout()
        lbl = QLabel(GuiLabels.label_userflow_settings)
        btn_confirm = QPushButton(GuiLabels.apply)
        btn_confirm.clicked.connect(self.close)

        self._view = QListWidget()
        self._view.setSelectionMode(MultiSelection)
        self._view.addItems(widgets)
        self.set_selected(selected_widgets)

        self._main_layout.addWidget(lbl)
        self._main_layout.addWidget(self._view)
        self._main_layout.addWidget(btn_confirm)

        self.setLayout(self._main_layout)

    def close(self):
        selected = self.selected()
        self.set.emit(selected)
        super().close()

    def set_selected(self, widgets: list[str] | tuple[str, ...]):
        for i in range(self._view.count()):
            item = self._view.item(i)
            if item.text() in widgets:
                self._view.setCurrentItem(item)

    def set_widgets(self, widgets: list[str]):
        self._view.addItems(widgets)

    def widgets(self) -> tuple[str, ...]:
        result = []
        for i in range(self._view.count()):
            item = self._view.item(i)
            result.append(item.text())

        return tuple(result)

    def selected(self) -> tuple[str, ...]:
        return tuple(item.text() for item in self._view.selectedItems())


if __name__ == '__main__':
    pass
