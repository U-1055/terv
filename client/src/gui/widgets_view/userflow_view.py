"""
Представления виджетов пользовательского пространства.
"""
import datetime
import time

from PySide6.QtCore import Signal, Qt, QSize, QTimer, QObject
from PySide6.QtWidgets import (QVBoxLayout, QListWidget, QDialog, QHBoxLayout, QPushButton, QAbstractItemView, QLabel,
                               QScrollArea, QWidget, QGraphicsScene, QSizePolicy)
from PySide6.QtGui import QFontMetrics, QBrush, QPen, QColor

import logging
import typing as tp

from client.src.gui.widgets_view.base_view import BaseView
from client.src.ui.ui_userflow_task_widget import Ui_Form as UserFlowTaskWidget
from client.src.ui.ui_userflow_notes_widget import Ui_Form as UserFlowNotesWidget
from client.src.ui.ui_userflow_schedule_widget import Ui_Form as UserFlowScheduleWidget
from client.src.gui.sub_widgets.widgets import UserFlowTask, Reminder, QEventWidget
from client.src.base import GuiLabels, DataStructConst, ObjectNames
from client.src.gui.sub_widgets.common_widgets import QStructuredText
from client.utils.data_tools import parse_time

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


class ScheduleWidgetView(BaseView):
    """
    Представление виджета расписания
    """

    def __init__(self, title: str = GuiLabels.schedule_widget):
        super().__init__()
        self._view = UserFlowScheduleWidget()
        self._view.setupUi(self)
        self._view.label.setText(title)
        self._view.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._view.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

        self._event_parent = QObject()
        self._graphics_size: QSize | None = None
        self._hour_step: int | None = None
        self._sub_step: int | None = None
        self._label_padding: int | None = None
        self._base_padding: int | None = None
        self._events: list[QEventWidget] = []
        self._current_event: QEventWidget | None = None

        self._set_marking()  # С задержкой, т.к. иначе виджет не успевает отрисоваться и будет некорректный размер
        QTimer.singleShot(50, self._reset_scene)  # Перерисовка сцены после окончательной отрисовки виджета (когда будут определены реальные размеры)

    def _set_marking(self):
        """Устанавливает разметку. Создаёт новую сцену."""

        self._get_fact_size()

        scene = QGraphicsScene()
        scene.setSceneRect(0, 0, self._graphics_size.width(), self._graphics_size.height())

        metrics = self.get_scene_font_metrics(scene)
        text_width = metrics[0] * 5
        text_height = metrics[1]

        padding = text_width + self._base_padding

        for i in range(24):
            line_height = i * self._hour_step // 1 + 0.5 * text_height  # 0.5 * text_height, чтобы линия оказывалась посередине надписи
            scene.addLine(padding, line_height, self._graphics_size.width(), line_height)

            lbl_height = line_height - 0.75 * text_height  # ToDo: проверить коэффициент 0.75 в разных конфигурациях окон
            text = datetime.time(hour=i, minute=0).strftime('%H:%M')
            lbl = scene.addText(text)
            lbl.setPos(0, lbl_height)

        self._view.graphicsView.setScene(scene)

    def _reset_scene(self):
        """Перерисовывает QGraphicsScene виджета."""
        self._set_marking()
        for event in self._events:
            self.add_custom_event(event)

    @staticmethod
    def get_scene_font_metrics(scene: QGraphicsScene) -> tuple[int, int]:
        """Возвращает ширину и высоту шрифта. Первое число - средняя ширина символа, второе - высота."""
        metrics = QFontMetrics(scene.font())
        return metrics.averageCharWidth(), metrics.height()

    def _get_fact_size(self):
        """Устанавливает фактический размер виджета."""
        self._graphics_size = self._view.graphicsView.size()
        self._hour_step = self._graphics_size.height() / 24  # Отступ линии часа  (Для повышения точности считаются без округления, округляются уже на месте)
        self._sub_step = self._hour_step / 4  # Отступ линии 15-ти минут
        self._base_padding = self._graphics_size.width() // 20  # Малый отступ (для добавления малой величины к координате)
        # Число 20 выбрано просто так (При делении на него получается достаточно малая величина)

    def _place_wdg_event(self, event: QEventWidget):
        self._get_fact_size()

        padding_steps = parse_time(event.time_start(), 15)  # 15 минут в интервале
        height_steps = parse_time(event.time_end(), 15) - padding_steps  # Высота виджета в 15-ти минутных интервалах

        scene = self._view.graphicsView.scene()
        text_width, text_height = self.get_scene_font_metrics(scene)
        text_width *= 5  # 5 - длина надписи в формате HH:MM
        first_line_padding = text_height * 0.5  # Отступ первой линии (соответствующей времени 00:00)
        v_padding = padding_steps * self._sub_step // 1 + first_line_padding

        h_padding = text_width + self._base_padding * 1.5  # Отступ для виджета (на всякий случай умножаем на 1.5, чтобы был чуть больше)
        event.setWindowOpacity(1)

        rect = scene.addRect(h_padding, v_padding, self._graphics_size.width() - h_padding,
                             height_steps)  # Настройка виджета

        rect.setFlag(rect.GraphicsItemFlag.ItemIsPanel)
        self._current_event = None

    def add_event(self, title: str, time_start: str, time_end: str, lasting: str,
                  wdg_description: dict = None, time_separator: str = GuiLabels.default_time_separator,
                  lasting_label: str = '', start_end_label: str = '', btn_show_details_label: str = ''):
        """
        Добавляет событие.
        :param title: название события.
        :param time_start: время начала.
        :param time_end: время окончания.
        :param lasting: длительность в формате H ч. M мин. (Например: 3 ч. 15 мин.)
        :param wdg_description: QStructuredText (client.src.gui.sub_widgets.common_widgets.QStructuredText), который
                                 выводится по нажатию на кнопку.
        :param lasting_label: надпись, показываемая перед длительностью.
        :param start_end_label: надпись, показываемая перед временем начала и окончания события.
        :param time_separator: разделитель между временем начала и временем конца.
        :param btn_show_details_label: надпись на кнопке подробностей.
        """
        event = QEventWidget(title, time_start, time_end, lasting, wdg_description, time_separator, lasting_label,
                       start_end_label,
                       btn_show_details_label)
        widget = QWidget()
        lbl = QLabel('TEXT')
        lbl.setParent(widget)
        self._get_fact_size()

        padding_steps = parse_time(event.time_start(), 15)  # 15 минут в интервале
        height_steps = parse_time(event.time_end(), 15) - padding_steps  # Высота виджета в 15-ти минутных интервалах
        # ToDo: выравнивание по нижней границе
        scene = self._view.graphicsView.scene()
        text_width, text_height = self.get_scene_font_metrics(scene)
        text_width *= 5  # 5 - длина надписи в формате HH:MM
        first_line_padding = text_height * 0.5  # Отступ первой линии (соответствующей времени 00:00)
        v_padding = padding_steps * self._sub_step // 1 + first_line_padding

        h_padding = text_width + self._base_padding * 1.5  # Отступ для виджета (на всякий случай умножаем на 1.5, чтобы был чуть больше)
        widget_ = scene.addWidget(lbl)
        widget_.setPos(h_padding, v_padding)
        self._current_event = None


    def add_custom_event(self, event: QEventWidget):
        """
        Добавляет событие
        :param event: экземпляр QEventWidget.
        """
        if not self._current_event:
            self._current_event = event
        if event not in self._events:
            self._events.append(event)
        self._get_fact_size()
        self._place_wdg_event(event)

    def delete_event(self, title: str):
        pass

    def clear(self):
        """Удаляет все события."""
        for event in self._events:
            event.hide()
            self._events.remove(event)

    def resizeEvent(self, event, /):  # При изменении размеров размер виджета пересчитывается
        last_params = self._graphics_size
        self._get_fact_size()
        if self._graphics_size.width() != last_params.width() or self._graphics_size.height() != last_params.height():
            self._reset_scene()  # Пересчитывается только при изменении параметров
        super().resizeEvent(event)


class ReminderWidgetView(BaseUserFlowWidget):
    reminder_added = Signal(str)  # Вызывается при добавлении напоминания. Возвращает название напоминания
    reminder_completed = Signal(str)  # Вызывается при закрытии напоминания. Возвращает название напоминания
    reminder_edited = Signal(str,
                             str)  # Вызывается при редактировании напоминания. Первая строка - предыдущее название напоминания, вторая - текущее

    def __init__(self, max_reminder_length: int = DataStructConst.max_reminder_length):
        super().__init__(DataStructConst.reminder_widget)
        self._max_reminder_length = max_reminder_length

        main_layout = QVBoxLayout()
        main_layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        header_layout = QHBoxLayout()
        header_layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)

        btn_add_widget = QPushButton(DataStructConst.char_plus)
        btn_add_widget.setObjectName(ObjectNames.small_btn_add)
        btn_add_widget.clicked.connect(self._on_btn_add_widget_pressed)
        lbl = QLabel(GuiLabels.reminder_widget, alignment=Qt.AlignmentFlag.AlignHCenter)

        header_layout.addWidget(lbl, 5)
        header_layout.addWidget(btn_add_widget, 1)

        self._widgets_layout = QVBoxLayout()
        self._widgets_layout.setDirection(QVBoxLayout.Direction.TopToBottom)
        scroll_area_content = QWidget()
        scroll_area = QScrollArea()

        scroll_area.setWidget(scroll_area_content)
        scroll_area_content.setLayout(self._widgets_layout)
        scroll_area.setWidgetResizable(True)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

    def _on_btn_add_widget_pressed(self):
        reminder = Reminder(GuiLabels.new_reminder, self._max_reminder_length)
        reminder.completed.connect(self.complete_reminder)
        self._widgets_layout.insertWidget(0, reminder)
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
        reminder = Reminder(label, self._max_reminder_length)
        reminder.completed.connect(self.complete_reminder)
        reminder.edited.connect(self.edit_reminder)
        self._widgets_layout.addWidget(reminder)

    def delete_reminder(self, label: str):
        for i in range(self._widgets_layout.count()):
            widget = self._widgets_layout.itemAt(i).widget()
            if widget.name == label:
                logging.debug(f'Reminder deleted: {widget.name}')
                widget.hide()

    def reminders(self) -> tuple[str, ...]:
        result = []
        for i in range(self._widgets_layout.count()):
            widget = self._widgets_layout.itemAt(i).widget()
            result.append(widget.name)

        return tuple(result)

    def set_max_reminder_length(self, length: int):
        self._max_reminder_length = length

    def max_reminder_length(self) -> int:
        return self._max_reminder_length


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
    from test.client_test.utils.window import setup_gui

    widget = ScheduleWidgetView()
    widget.add_event('Name', '14:15', '14:45', '45 мин.')
    setup_gui(widget)

