import logging

from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QMenu, QWidgetAction, QFrame
from PySide6.QtCore import Signal, QObject, Qt, QPoint

from client.src.base import DataStructConst, GuiLabels, ObjectNames
from client.src.ui.ui_event_widget import Ui_Form as EventView
from client.src.gui.sub_widgets.common_widgets import QStructuredText
from client.src.gui.sub_widgets.util_widgets import QMouseActivatingLineEdit, QClickableLabel


class UserSpaceTask(QWidget):
    """
    Виджет задачи ПП.

    :param name: Название задачи.
    :param type_: Тип задачи.
    :param id_: ID задачи
    :param wdg_description: Структурированный текст (как в QStructuredText), выводимый при нажатии на задачу.

    """
    completed = Signal(str, int)  # Вызывается при нажатии на кнопку выполнения задачи. Возвращает тип задачи и её ID.

    def __init__(self, name: str, type_: str, id_: int, wdg_description: dict = None):
        super().__init__()
        if wdg_description:
            self._structured_text = QStructuredText(wdg_description)
        else:
            self._structured_text = None
        self._id = id_
        self._type = type_

        main_layout = QHBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._lbl_name = QClickableLabel(name)
        self._lbl_name.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._lbl_name.customContextMenuRequested.connect(self._on_lbl_clicked)

        self._btn_complete = QPushButton()
        self._btn_complete.clicked.connect(self.complete_task)

        main_layout.addWidget(self._lbl_name, 5)
        main_layout.addWidget(self._btn_complete, 1)

        self.setLayout(main_layout)

    def _on_lbl_clicked(self, pos: QPoint):
        menu = QMenu(parent=self._lbl_name)
        action = QWidgetAction(menu)
        action.setDefaultWidget(self._structured_text)
        menu.addAction(action)
        menu.exec(self._lbl_name.mapToGlobal(pos))  # Переводим координаты виджета в абсолютные

    def complete_task(self):
        self.completed.emit(self._type, self._id)

    def name(self) -> str:
        return self._lbl_name.text()

    def set_name(self, name: str):
        self._lbl_name.setText(name)

    def type(self):
        return self._type

    def set_type(self, type_: str):
        self._type = type_

    def id(self) -> int:
        return self._id

    def set_id(self, id_: int):
        self._id = id_


class Reminder(QWidget):
    """Виджет напоминания."""

    completed = Signal(QWidget)  # Напоминание закрыто. Возвращается виджет
    edited = Signal(str, str)  # Название редактировано. Первая строка - старое название, вторая - новое

    def __init__(self, label: str, max_length: int = DataStructConst.max_reminder_length):
        super().__init__()
        self.name = label
        self._main_layout = QHBoxLayout()
        self._line_edit_lbl = QMouseActivatingLineEdit(label, max_length)
        self._line_edit_lbl.editingFinished.connect(self.edit)
        btn_complete = QPushButton()
        btn_complete.clicked.connect(self.complete)

        self._main_layout.addWidget(btn_complete)
        self._main_layout.addWidget(self._line_edit_lbl)
        self.setLayout(self._main_layout)

    def edit(self):
        name = self._line_edit_lbl.text()
        self.edited.emit(self.name, name)
        self.name = name

    def complete(self):
        self.completed.emit(self)

    def setFocus(self):
        self._line_edit_lbl.setFocus()

    def setReadOnly(self, arg: bool):
        self._line_edit_lbl.setReadOnly(arg)


class QEventWidget(QWidget):
    """
    Виджет события календаря.

    :param title: название события.
    :param time_start: время начала.
    :param time_end: время окончания.
    :param wdg_description: словарь, содержащий описание структурированного текста (как в QStructuredText),
                            который выводится при нажатии на событие. Словарь вида: {<название поля>: <текст>}.
    :param lasting_label: надпись, показываемая перед длительностью.
    :param start_end_label: надпись, показываемая перед временем начала и окончания события.
    """

    tooltip_field_clicked = Signal(str)  # Вызывается при нажатии на поле wdg_description. Возвращает название поля
    tooltip_content_clicked = Signal(str)  # Вызывается при нажатии на текст поля wdg_description. Возвращает название поля

    def __init__(self, title: str, time_start: str, time_end: str,
                 wdg_description: dict = None, time_separator: str = GuiLabels.default_time_separator,
                 start_end_label: str = '', btn_show_details_label: str = '', parent: QWidget = None):
        super().__init__(parent=parent)
        self.setObjectName(ObjectNames.wdg_border)

        self._parent = parent
        self._title = title
        self._time_start = time_start
        self._time_end = time_end
        if wdg_description:
            self._wdg_description = QStructuredText(wdg_description)
            self._wdg_description.field_clicked.connect(self._on_tooltip_field_clicked)
            self._wdg_description.content_clicked.connect(self._on_tooltip_content_clicked)
        else:
            self._wdg_description = None
        self._time_separator = time_separator
        self._start_end_label = start_end_label
        self._btn_show_details_label = btn_show_details_label

        self._view = EventView()
        self._view.setupUi(self)

        self._view.btn_show_details.clicked.connect(self._on_btn_show_details_clicked)
        self._view.btn_show_details.setText(self._btn_show_details_label)
        self._view.btn_show_details.setObjectName(ObjectNames.btn_show_details)

        self._set_menu()
        self._setup_widgets()

    def _set_menu(self):
        """Настраивает меню для кнопки (wdg_description)."""

        self._menu = QMenu()  # Настройка меню (wdg_description, которое показывается при нажатии на кнопку)
        widget_action = QWidgetAction(self._menu)  # self._menu, а не просто локальная переменная, т.к иначе сборщик мусора удаляет её
        widget_action.setDefaultWidget(self._wdg_description)
        self._menu.addAction(widget_action)
        self._view.btn_show_details.setMenu(self._menu)

    def _on_btn_show_details_clicked(self):
        """Показать подробности (wdg_description)."""
        self._view.btn_show_details.menu()

    def _on_tooltip_field_clicked(self, field: str):
        self.tooltip_field_clicked.emit(field)

    def _on_tooltip_content_clicked(self, field: str):
        self.tooltip_content_clicked.emit(field)

    def _setup_widgets(self):
        self._view.lbl_start_end.setText(f'{self._start_end_label}{self._time_start}{self._time_separator}{self._time_end}')
        self._view.lbl_title.setText(self._title)
    
    def title(self) -> str:
        return self._title
    
    def set_title(self, title: str):
        self._title = title
        self._view.lbl_title.setText(self._title)

    def set_time_start(self, time_start: str):
        self._time_start = time_start
        self._view.lbl_start_end.setText(
            f'{self._start_end_label}{self._time_start}{self._time_separator}{self._time_end}')
    
    def time_start(self) -> str:
        return self._time_start

    def set_time_end(self, time_end: str):
        self._time_end = time_end
        self._view.lbl_start_end.setText(
            f'{self._start_end_label}{self._time_start}{self._time_separator}{self._time_end}')

    def time_end(self) -> str:
        return self._time_end

    def wdg_description(self) -> QStructuredText | None:
        if self._wdg_description:
            return self._wdg_description

    def set_wdg_description(self, wdg_description: dict | None):
        if wdg_description is not None:
            self._wdg_description = QStructuredText(wdg_description)
            self._set_menu()
        else:
            self._wdg_description = None

    def set_time_separator(self, time_separator: str):
        self._time_separator = time_separator
        self._view.lbl_start_end.setText(
            f'{self._start_end_label}{self._time_start}{self._time_separator}{self._time_end}')

    def time_separator(self) -> str:
        return self._time_separator

    def set_start_end_label(self, start_end_label: str):
        self._start_end_label = start_end_label
        self._view.lbl_start_end.setText(
            f'{self._start_end_label}{self._time_start}{self._time_separator}{self._time_end}')

    def start_end_label(self) -> str:
        return self._start_end_label

    def set_btn_show_details_label(self, btn_show_details_label: str):
        self._btn_show_details_label = btn_show_details_label
        self._view.btn_show_details.setText(btn_show_details_label)

    def btn_show_details_label(self) -> str:
        return self._btn_show_details_label


if __name__ == '__main__':
    from test.client_test.utils.window import setup_gui
    wdg = UserSpaceTask('name', '1', 2, {'1': '1111111', 'GGG': '1342'})
    setup_gui(wdg)

