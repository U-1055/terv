import logging

from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QMenu, QWidgetAction
from PySide6.QtCore import Signal, QObject

from client.src.base import DataStructConst, GuiLabels
from client.src.ui.ui_event_widget import Ui_Form as EventView
from client.src.gui.sub_widgets.common_widgets import QStructuredText
from client.src.gui.sub_widgets.util_widgets import QMouseActivatingLineEdit


class UserFlowTask(QWidget):
    completed = Signal(str)

    def __init__(self, name: str):
        super().__init__()

        main_layout = QHBoxLayout()

        self._lbl_name = QLabel(name)
        self._btn_complete = QPushButton()
        self._btn_complete.clicked.connect(self.complete_task)

        main_layout.addWidget(self._lbl_name, 5)
        main_layout.addWidget(self._btn_complete, 1)

        self.setLayout(main_layout)

    def complete_task(self):
        self.completed.emit(self._lbl_name)

    def name(self) -> str:
        return self._lbl_name.text()

    def set_name(self, name: str):
        self._lbl_name.setText(name)


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
    :param lasting: длительность в формате H ч. M мин. (Например: 3 ч. 15 мин.)
    :param wdg_description: QStructuredText (client.src.gui.sub_widgets.common_widgets.QStructuredText), который
    выводится по нажатию на кнопку.
    :param lasting_label: надпись, показываемая перед длительностью.
    :param start_end_label: надпись, показываемая перед временем начала и окончания события.
    """

    def __init__(self, parent: QWidget, title: str, time_start: str, time_end: str, lasting: str,
                 wdg_description: QStructuredText = None, time_separator: str = GuiLabels.default_time_separator,
                 lasting_label: str = '', start_end_label: str = '', btn_show_details_label: str = ''):
        super().__init__(parent=parent)

        self._parent = parent
        self._title = title
        self._time_start = time_start
        self._time_end = time_end
        self._lasting = lasting
        self._wdg_description = wdg_description
        self._time_separator = time_separator
        self._lasting_label = lasting_label
        self._start_end_label = start_end_label
        self._btn_show_details_label = btn_show_details_label

        self._view = EventView()
        self._view.setupUi(self)
        self._view.btn_show_details.clicked.connect(self._on_btn_show_details_clicked)
        self._view.btn_show_details.setText(self._btn_show_details_label)

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

    def _setup_widgets(self):
        self._view.lbl_start_end.setText(f'{self._start_end_label}{self._time_start}{self._time_separator}{self._time_end}')
        self._view.lbl_title.setText(self._title)
        self._view.lbl_lasting.setText(f'{self._lasting_label}{self._lasting}')
    
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
    
    def lasting(self) -> str:
        return self._lasting
    
    def set_lasting(self, lasting: str):
        self._lasting = lasting
        self._view.lbl_lasting.setText(f'{self._lasting_label}{self._lasting}')

    def wdg_description(self) -> QStructuredText | None:
        return self._wdg_description

    def set_wdg_description(self, wdg_description: QStructuredText):
        self._wdg_description = wdg_description
        self._set_menu()

    def set_time_separator(self, time_separator: str):
        self._time_separator = time_separator
        self._view.lbl_start_end.setText(
            f'{self._start_end_label}{self._time_start}{self._time_separator}{self._time_end}')

    def time_separator(self) -> str:
        return self._time_separator

    def set_lasting_label(self, lasting_label: str):
        self._lasting = lasting_label
        self._view.lbl_lasting.setText(f'{self._lasting_label}{self._lasting}')

    def lasting_label(self) -> str:
        return self._lasting_label

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

    task_info = QStructuredText(
        {
            'Описание': ''.join([f'{''.join(['C' for i in range(10)])} ' for x in range(100)]),
            'Создатель': ''.join(['n' for i in range(30)]),
            'Поручил': ''.join(['n' for i in range(30)])
        }
    )

    event = QEventWidget('some_text', '14:15', '14:20', '5 мин.', task_info, '-', GuiLabels.lasting_label,
                   GuiLabels.start_end_label)
    setup_gui(event)

