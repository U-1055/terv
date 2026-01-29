from PySide6.QtWidgets import QHBoxLayout, QGridLayout, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal

import logging

from client.src.base import GuiLabels, DataStructConst
from client.src.gui.widgets_view.userflow_view import (TaskWidgetView, NotesWidgetView, ScheduleWidgetView, 
                                                       BaseUserFlowWidget, ReminderWidgetView)
from client.src.gui.windows.windows import BaseWindow
from client.src.gui.aligns import AlignBottom, AlignRight
from client.utils.qt_utils import filled_rows_count, filled_columns_count


class UserFlowWindow(BaseWindow):
    """
    Окно ПП. Размещает настраиваемые виджеты в соответствии с параметрами:
    x - столбец; y - строка; x_size - число занимаемых виджетов столбцов; y_size - число занимаемых виджетом строк.
    """

    btn_set_widgets_pressed = Signal()

    def __init__(self):
        super().__init__()
        self._tasks_widget: TaskWidgetView | None = None
        self._notes_widget: NotesWidgetView | None = None
        self._reminder_widget: ReminderWidgetView | None = None

        self._main_layout = QHBoxLayout()
        self._widgets_layout = QGridLayout()
        self._schedule_layout = QVBoxLayout()

        self._last_x = 0  # Координаты последнего размещённого виджета на сетке
        self._last_y = 0

        btn_set_widgets = QPushButton(GuiLabels.userflow_settings)
        btn_set_widgets.clicked.connect(self.press_btn_set_widgets)

        self._main_layout.addLayout(self._widgets_layout, 5)
        self._main_layout.addLayout(self._schedule_layout, 1)
        self._main_layout.addWidget(btn_set_widgets, 1, alignment=AlignBottom)

        self.setLayout(self._main_layout)

        logging.debug('UserFlowWindow initialized')

    def press_btn_set_widgets(self):
        self.btn_set_widgets_pressed.emit()

    def _prepare_params(self, x: int, y: int, x_size: int, y_size: int) -> list[int]:
        result = []
        for param in [x_size, y_size]:
            if param is None:
                param = 0
            result.append(param)

        return [x, y, x_size, y_size]

    def _place_settable_widget(self, widget: BaseUserFlowWidget, x: int, y: int, x_size: int, y_size: int):
        if not x and not y:
            x = filled_columns_count(self._widgets_layout) + 1
            y = filled_rows_count(self._widgets_layout)
            if y > DataStructConst.max_y_size:
                y = 0

            if x > DataStructConst.max_x_size:
                x = 0   # Случай, когда y превышает max_y_size не рассматривается,
                y += 1  # поскольку в программе пока не может быть столько виджетов ПП
            logging.debug(f'Coordinates for widget {widget.name} computed: x: {x}; y: {y}')

            self._widgets_layout.addWidget(widget, y, x)
        else:
            self._widgets_layout.addWidget(widget, y, x, y_size, x_size)

    def place_task_widget(self, x: int = 0, y: int = 0, x_size: int = 1, y_size: int = 1) -> TaskWidgetView:
        """
        Размещает виджет задач.
        :param x: столбец.
        :param y: строка.
        :param x_size: число занимаемых виджетом столбцов.
        :param y_size: число занимаемых виджетом строк.
        """

        x, y, x_size, y_size = self._prepare_params(x, y, x_size, y_size)
        logging.debug(f'Task widget placed with coords: (x: {x}, y: {y}, x_size: {x_size}, y_size: {y_size})')

        self._tasks_widget = TaskWidgetView()
        self._place_settable_widget(self._tasks_widget, x, y, x_size, y_size)
        return self._tasks_widget

    def place_schedule_widget(self) -> ScheduleWidgetView:
        widget = ScheduleWidgetView()
        self._schedule_layout.addWidget(widget)
        return widget

    def place_notes_widget(self, x: int = 0, y: int = 0, x_size: int = 1,
                           y_size: int = 1) -> NotesWidgetView:
        """
        Размещает виджет заметок.
        :param x: столбец.
        :param y: строка.
        :param x_size: число занимаемых виджетом столбцов.
        :param y_size: число занимаемых виджетом строк.
        """

        x, y, x_size, y_size = self._prepare_params(x, y, x_size, y_size)
        logging.debug(f'Notes widget placed with coords: (x: {x}, y: {y}, x_size: {x_size}, y_size: {y_size})')
        self._notes_widget = NotesWidgetView()
        self._place_settable_widget(self._notes_widget, x, y, x_size, y_size)
        return self._notes_widget

    def place_reminder_widget(self, x: int = 0, y: int = 0, x_size: int = 1, y_size: int = 1) -> ReminderWidgetView:
        """
        Размещает виджет напоминаний.
        :param x: столбец.
        :param y: строка.
        :param x_size: число занимаемых виджетом столбцов.
        :param y_size: число занимаемых виджетом строк.
        """

        x, y, x_size, y_size = self._prepare_params(x, y, x_size, y_size)
        logging.debug(f'reminder widget placed with coords: (x: {x}, y: {y}, x_size: {x_size}, y_size: {y_size})')
        self._reminder_widget = ReminderWidgetView()
        self._place_settable_widget(self._reminder_widget, x, y, x_size, y_size)
        return self._reminder_widget

    def delete_notes_widget(self):
        if self._notes_widget:
            self._notes_widget.hide()
            self._notes_widget = None

    def delete_reminder_widget(self):
        if self._reminder_widget:
            self._reminder_widget.hide()
            self._reminder_widget = None

    def delete_tasks_widget(self):
        if self._tasks_widget:
            self._tasks_widget.hide()
            self._tasks_widget = None

    def close(self):
        super().close()
        logging.debug('UserFlowWindow closed')
