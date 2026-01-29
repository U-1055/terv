"""
Представления виджетов пользовательского пространства.
"""
import typing as tp

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (QVBoxLayout, QListWidget, QDialog, QHBoxLayout, QPushButton, QAbstractItemView, QLabel,
                               QScrollArea, QWidget)
from client.src.gui.widgets_view.base_view import BaseView
from client.src.ui.ui_userflow_task_widget import Ui_Form as UserFlowTaskWidget
from client.src.ui.ui_userflow_notes_widget import Ui_Form as UserFlowNotesWidget
from client.src.gui.sub_widgets.widgets import UserFlowTask, Reminder
from client.src.base import GuiLabels, DataStructConst, ObjectNames

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


class ScheduleWidgetView(BaseView):  # ToDo: сам виджет + вспомогательные виджеты

    def __init__(self):
        super().__init__()


class ReminderWidgetView(BaseUserFlowWidget):

    reminder_added = Signal(str)  # Вызывается при добавлении напоминания. Возвращает название напоминания
    reminder_completed = Signal(str)  # Вызывается при закрытии напоминания. Возвращает название напоминания
    reminder_edited = Signal(str, str)  # Вызывается при редактировании напоминания. Первая строка - предыдущее название напоминания, вторая - текущее

    def __init__(self):
        super().__init__(DataStructConst.reminder_widget)

        main_layout = QVBoxLayout()
        main_layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        header_layout = QHBoxLayout()
        header_layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)

        btn_add_widget = QPushButton(DataStructConst.char_plus)
        btn_add_widget.setObjectName(ObjectNames.small_btn_add)
        btn_add_widget.clicked.connect(self._on_btn_add_widget_pressed)
        lbl = QLabel(GuiLabels.reminder_widget, alignment=Qt.AlignmentFlag.AlignHCenter)

        header_layout.addWidget(lbl, 5)
        header_layout.addWidget(btn_add_widget, 1)


        self._widgets_layout = QVBoxLayout()
        scroll_area_content = QWidget()
        scroll_area = QScrollArea()

        scroll_area.setWidget(scroll_area_content)
        scroll_area_content.setLayout(self._widgets_layout)
        # ToDo: скроллинг
        main_layout.addLayout(header_layout)
        main_layout.addWidget(scroll_area_content)

        self.setLayout(main_layout)

    def _on_btn_add_widget_pressed(self):
        reminder = Reminder(GuiLabels.new_reminder)
        reminder.completed.connect(self.complete_reminder)
        self._widgets_layout.addWidget(reminder)
        reminder.setFocus()
        reminder.setReadOnly(False)
        self.reminder_added.emit(reminder.name)

    def edit_reminder(self, last_name: str, next_name: str):
        self.reminder_edited.emit(last_name, next_name)

    def complete_reminder(self, reminder: Reminder):
        self.reminder_completed.emit(reminder.name)
        reminder.hide()

    def set_reminders(self, labels: tuple[str, ...] | list[str]):
        for label in labels:
            self.add_reminder(label)

    def add_reminder(self, label: str):
        reminder = Reminder(label)
        reminder.completed.connect(self.complete_reminder)
        reminder.edited.connect(self.edit_reminder)
        self._widgets_layout.addWidget(reminder)

    def delete_reminder(self, label: str):
        for i in range(self._widgets_layout.count()):
            widget = self._widgets_layout.itemAt(i).widget()
            if widget.name == label:
                widget.hide()

    def reminders(self) -> tuple[str, ...]:
        result = []
        for i in range(self._widgets_layout.count()):
            widget = self._widgets_layout.itemAt(i).widget()
            result.append(widget.name)

        return tuple(result)


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
                item.setSelected(True)

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
