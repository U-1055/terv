from PySide6.QtWidgets import QHBoxLayout, QGridLayout, QVBoxLayout, QPushButton

import logging

from client.src.base import GuiLabels
from client.src.gui.widgets_view.userflow_view import TaskWidgetView, NotesWidgetView, ScheduleWidgetView
from client.src.gui.windows.windows import BaseWindow


class UserFlowWindow(BaseWindow):
    """
    Окно ПП. Размещает настраиваемые виджеты в соответствии с параметрами:
    x - столбец; y - строка; x_size - число занимаемых виджетов столбцов; y_size - число занимаемых виджетом строк.
    """

    def __init__(self):
        super().__init__()
        self._main_layout = QHBoxLayout()
        self._widgets_layout = QGridLayout()
        self._schedule_layout = QVBoxLayout()

        self._main_layout.addLayout(self._widgets_layout, 5)
        self._main_layout.addLayout(self._schedule_layout, 1)

        self.setLayout(self._main_layout)

        logging.debug('UserFlowWindow initialized')

    def _prepare_params(self, params: tuple[int, ...] | list[int]) -> list[int]:
        result = []
        for param in params:
            if param is None:
                param = 0
            result.append(param)
        return result

    def place_task_widget(self, x: int = 0, y: int = 0, x_size: int = 1, y_size: int = 1) -> TaskWidgetView:
        """
        Размещает виджет задач.
        :param x: столбец.
        :param y: строка.
        :param x_size: число занимаемых виджетом столбцов.
        :param y_size: число занимаемых виджетом строк.
        """
        x, y, x_size, y_size = self._prepare_params([x, y, x_size, y_size])
        widget = TaskWidgetView()
        self._widgets_layout.addWidget(widget, y, x, y_size, x_size)
        return widget

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
        x, y, x_size, y_size = self._prepare_params([x, y, x_size, y_size])
        widget = NotesWidgetView()
        self._widgets_layout.addWidget(widget, y, x, y_size, x_size)
        return widget

    def close(self):
        super().close()
        logging.debug('UserFlowWindow closed')
