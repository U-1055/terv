from PySide6.QtWidgets import QHBoxLayout, QGridLayout, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor

import logging

from client.src.base import GuiLabels, DataStructConst
from client.src.gui.widgets_view.userspace_view import (TaskWidgetView, NotesWidgetView, ScheduleWidgetView, 
                                                       BaseUserSpaceWidget, ReminderWidgetView, EventsTodayWidget)
from client.src.gui.windows.windows import BaseWindow
from client.src.gui.aligns import AlignBottom
from client.utils.qt_utils import filled_rows_count, filled_columns_count, get_next_widget_grid_pos


class UserSpaceWindow(BaseWindow):
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
        self._schedule_widget: ScheduleWidgetView | None = None
        self._events_today_widget: EventsTodayWidget | None = None

        self._tasks_widget_pos: tuple[int, int] | None = None
        self._notes_widget_pos: tuple[int, int] | None = None
        self._reminder_widget_pos: tuple[int, int] | None = None

        self._main_layout = QHBoxLayout()
        self._widgets_layout = QGridLayout()
        self._schedule_layout = QVBoxLayout()

        self._last_x = -1  # Координаты последнего размещённого виджета на сетке (Вначале виджета нет, поэтому -1)
        self._last_y = 0

        btn_set_widgets = QPushButton(GuiLabels.userspace_settings)
        btn_set_widgets.clicked.connect(self.press_btn_set_widgets)

        self._main_layout.addLayout(self._widgets_layout, 10)
        self._main_layout.addWidget(btn_set_widgets, 1, alignment=AlignBottom)
        self._main_layout.addLayout(self._schedule_layout, 8)

        self.setLayout(self._main_layout)

        logging.debug('UserSpaceWindow initialized')

    def press_btn_set_widgets(self):
        self.btn_set_widgets_pressed.emit()

    def _prepare_params(self, x: int, y: int, x_size: int, y_size: int) -> list[int]:
        result = []
        for param in [x_size, y_size]:
            if param is None:
                param = 0
            result.append(param)

        return [x, y, x_size, y_size]

    def _place_settable_widget(self, widget: BaseUserSpaceWidget) -> tuple[int, int]:

        # Выбор новой позиции (следующий столбец или строка) зависит от заполненности виджета
        y, x = self._last_y, self._last_x
        if x < DataStructConst.max_x_size - 1:  # -1, т.к. max_x_size считается с 0
            x += 1
        else:
            y += 1
            x = 0

        logging.info(f'Coordinates for widget {widget.name} computed: x: {x}; y: {y}')
        self._widgets_layout.addWidget(widget, y, x)
        self._last_y, self._last_x = y, x  # Новая позиция последнего виджета
        return y, x

    def place_task_widget(self, tooltip_style_sheet: str = '') -> TaskWidgetView:
        """Размещает виджет задач."""
        self._tasks_widget = TaskWidgetView(tooltip_style_sheet)
        self._tasks_widget_pos = self._place_settable_widget(self._tasks_widget)
        return self._tasks_widget

    def place_schedule_widget(self, marking_color: QColor = QColor('black'),
                              events_style_sheet: str | None = None) -> ScheduleWidgetView:
        widget = ScheduleWidgetView(marking_color=marking_color, events_style_sheet=events_style_sheet)
        self._schedule_widget = widget
        self._schedule_layout.insertWidget(1, widget, 10)
        return widget

    def place_notes_widget(self) -> NotesWidgetView:
        """Размещает виджет заметок."""
        self._notes_widget = NotesWidgetView()
        self._notes_widget_pos = self._place_settable_widget(self._notes_widget)
        return self._notes_widget

    def place_reminder_widget(self) -> ReminderWidgetView:
        """Размещает виджет напоминаний."""
        self._reminder_widget = ReminderWidgetView()
        self._reminder_widget_pos = self._place_settable_widget(self._reminder_widget)
        return self._reminder_widget

    def place_events_today_widget(self, tooltip_style_sheet: str) -> EventsTodayWidget:
        """Размещает виджет многодневных событий."""
        self._events_today_widget = EventsTodayWidget(tooltip_style_sheet=tooltip_style_sheet)
        self._schedule_layout.insertWidget(0, self._events_today_widget, 1)
        return self._events_today_widget

    def delete_notes_widget(self):
        if self._notes_widget:
            if self._notes_widget_pos:
                self._last_y, self._last_x = self._notes_widget_pos
            self._notes_widget.hide()
            self._notes_widget = None

    def delete_reminder_widget(self):
        if self._reminder_widget:
            if self._reminder_widget_pos:
                self._last_y, self._last_x = self._reminder_widget_pos
            self._reminder_widget.hide()
            self._reminder_widget = None

    def delete_tasks_widget(self):
        if self._tasks_widget:
            if self._tasks_widget_pos:
                self._last_y, self._last_x = self._tasks_widget_pos
            self._tasks_widget.hide()
            self._tasks_widget = None

    def delete_schedule_widget(self):
        if self._schedule_widget:
            self._schedule_widget.hide()
            self._schedule_widget = None

    def delete_events_today_widget(self):
        if self._events_today_widget:
            self._events_today_widget.hide()
            self._events_today_widget = None

    def close(self):
        super().close()
        logging.debug('UserSpaceWindow closed')
