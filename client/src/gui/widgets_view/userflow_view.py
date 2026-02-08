"""
Представления виджетов пользовательского пространства.
"""
import datetime
import time

from PySide6.QtCore import Signal, Qt, QSize, QTimer, QObject
from PySide6.QtWidgets import (QVBoxLayout, QListWidget, QDialog, QHBoxLayout, QPushButton, QAbstractItemView, QLabel,
                               QScrollArea, QWidget, QGraphicsScene, QSizePolicy)
from PySide6.QtGui import QFontMetrics, QTextOption, QColor, QPen, QBrush

import logging
import typing as tp

from client.src.gui.widgets_view.base_view import BaseView
from client.src.ui.ui_userflow_task_widget import Ui_Form as UserFlowTaskWidget
from client.src.ui.ui_userflow_notes_widget import Ui_Form as UserFlowNotesWidget
from client.src.ui.ui_userflow_schedule_widget import Ui_Form as UserFlowScheduleWidget
from client.src.gui.sub_widgets.widgets import UserFlowTask, Reminder, QEventWidget
from client.src.base import GuiLabels, DataStructConst, ObjectNames
from client.utils.data_tools import parse_time
from client.src.gui.sub_widgets.common_widgets import QToolTipLabel

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
    """
    Виджет задач. Позволяет добавлять и выполнять задачи. Задачи разделяются на типы и идентифицируются по ID.
    (Это позволяет иметь задачи с одинаковыми именами). Задачи одного типа должны иметь разные ID.
    """

    task_completed = Signal(str, int)  # Вызывается при выполнении задачи. Возвращает тип задачи и её ID.

    def __init__(self):
        super().__init__(DataStructConst.tasks_widget)
        self._view = UserFlowTaskWidget()
        self._view.setupUi(self)
        self._view.label.setText(GuiLabels.tasks_widget)
        self._tasks_layout = QVBoxLayout()
        self._view.scrollArea.setWidget(self._view.scrollAreaWidgetContents)
        self._view.scrollAreaWidgetContents.setLayout(self._tasks_layout)
        self._tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Ignored)

        self._tasks_struct: dict[str, dict] = dict()

    def complete_task(self, type_: str, id_: int):
        widget = self._tasks_struct[type_][id_]

        widget.hide()
        self.task_completed.emit(type_, id_)

    def add_task(self, name: str, id_: int, type_: str, task_description: dict = None):
        """
        Добавляет задачу в виджет.
        (Параметры type_ и id_ нужны для однозначной идентификации задачи при её выполнении).

        :param name: Название задачи.
        :param id_: ID задачи.
        :param type_: Тип задачи.
        :param task_description: Структурированный текст, появляющийся в контекстном меню при нажатии на задачу.
                                 Текст вида {<название поля>: <текст поля>}.

        """
        widget = UserFlowTask(name, type_, id_, task_description)

        if type_ not in self._tasks_struct:  # Обновление структуры задач
            self._tasks_struct[type_] = {id_: widget}
        else:
            if id_ not in self._tasks_struct[type_]:
                self._tasks_struct[type_][id_] = widget
            else:
                raise ValueError(f"Task's id {id_} must be unique. (Task: name: {name}, id: {id_}, type: {type_})."
                                 f"Tasks struct: {self._tasks_struct}")
        widget.completed.connect(self.complete_task)
        self._tasks_layout.addWidget(widget)

    def set_tasks(self):
        self.clear()

    def clear(self):
        """Удаляет все задачи из виджета."""
        for i in range(self._view.verticalLayout_2.count()):
            wdg = self._view.verticalLayout_2.itemAt(i).widget()
            if wdg:
                wdg.hide()
        self._tasks_struct = dict()

    def to_loading_state(self):
        pass

    def to_normal_state(self):
        pass


class NotesWidgetView(BaseUserFlowWidget):
    """
    Виджет заметки.

    :var text_changed: Сигнал, вызываемый при редактировании текста в виджете.

    """

    text_changed = Signal()

    def __init__(self):
        super().__init__(DataStructConst.notes_widget)
        self._view = UserFlowNotesWidget()
        self._view.setupUi(self)
        self._view.label.setText(GuiLabels.notes_widget)
        self._view.textEdit.textChanged.connect(self._on_text_changed)
        self._view.textEdit.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)

    def _on_text_changed(self):
        self.text_changed.emit()

    def set_notes(self, text: str):
        self._view.textEdit.setText(text)

    def notes(self) -> str:
        return self._view.textEdit.toPlainText()


class ScheduleWidgetView(BaseView):
    """
    Виджет расписания.

    :var event_tooltip_field_clicked: Сигнал, вызывающийся при нажатии на поле подсказки события. Передаёт аргументами:
                                      id_ события, тип события, название поля.
    :var event_tooltip_content_clicked: Сигнал, вызывающийся при нажатии на текст поля подсказки события.
                                        Передаёт аргументами: id_ события, тип события, название поля.
    :param marking_color: Цвет элементов разметки (линий и подписей времени).
    """

    event_tooltip_field_clicked = Signal(int, str, str)
    event_tooltip_content_clicked = Signal(int, str, str)

    def __init__(self, title: str = GuiLabels.schedule_widget, marking_color: QColor = QColor('black'),
                 events_style_sheet: str | None = None):
        super().__init__()
        self._view = UserFlowScheduleWidget()
        self._view.setupUi(self)
        self._view.label.setText(title)
        self._view.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._view.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

        self._event_parent = QObject()
        self._marking_color = marking_color
        self._events_style_sheet = events_style_sheet
        self._graphics_size: QSize | None = None
        self._hour_step: int | None = None
        self._sub_step: int | None = None
        self._label_padding: int | None = None
        self._base_padding: int | None = None
        self._events: dict[str, dict[int, QEventWidget]] = dict()
        self._current_event: QEventWidget | None = None

        self._set_marking()  # С задержкой, т.к. иначе виджет не успевает отрисоваться и будет некорректный размер
        QTimer.singleShot(50, self._reset_scene)  # Перерисовка сцены после окончательной отрисовки виджета (когда будут определены реальные размеры)

    def _on_event_tooltip_field_clicked(self, id_: int, type_: str, field: str):
        self.event_tooltip_field_clicked.emit(id_, type_, field)

    def _on_event_tooltip_content_clicked(self, id_: int, type_: str, field: str):
        self.event_tooltip_content_clicked.emit(id_, type_, field)

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
            scene.addLine(padding, line_height, self._graphics_size.width(), line_height, self._marking_color)

            lbl_height = line_height - 0.75 * text_height  # ToDo: проверить коэффициент 0.75 в разных конфигурациях окон
            text = datetime.time(hour=i, minute=0).strftime('%H:%M')
            lbl = scene.addText(text)
            lbl.setDefaultTextColor(self._marking_color)
            lbl.setPos(0, lbl_height)

        self._view.graphicsView.setScene(scene)

    def _reset_scene(self):
        """Перерисовывает QGraphicsScene виджета."""
        self._set_marking()
        for type_ in self._events:
            for id_ in self._events[type_]:
                event = self._events[type_][id_]
                self.add_custom_event(event, id_, type_)

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

    def _place_wdg_event(self, event: QEventWidget, id_: int, type_: str):
        """Размещает виджет события."""
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
        # Виджет создаётся заново, потому что хранимые виджеты не настраиваются, т.к. их родителем является ScheduleWidget
        # Если виджеты будут без родителя, они удаляются Qt.

        event = QEventWidget(event.title(), event.time_start(), event.time_end(),
                             event.wdg_description(), event.time_separator(),
                             event.start_end_label(), event.btn_show_details_label())
        event.tooltip_field_clicked.connect(lambda field: self._on_event_tooltip_field_clicked(id_, type_, field))
        event.tooltip_field_clicked.connect(lambda field: self._on_event_tooltip_content_clicked(id_, type_, field))

        if self._events_style_sheet:
            event.setStyleSheet(self._events_style_sheet)

        rect = scene.addWidget(event)  # Настройка виджета
        rect.setPos(h_padding, v_padding)

        rect.setFlag(rect.GraphicsItemFlag.ItemIsPanel)

    def add_event(self, id_: int, type_: str, title: str, time_start: str, time_end: str, wdg_description: dict = None,
                  time_separator: str = GuiLabels.default_time_separator, start_end_label: str = '',
                  btn_show_details_label: str = ''):
        """
        Добавляет событие.

        :param id_: ID события.
        :param type_: Тип события
        :param title: Название события.
        :param time_start: Время начала.
        :param time_end: Время окончания.
        :param wdg_description: Cловарь, содержащий описание структурированного текста (как в QStructuredText),
                                который выводится при нажатии на событие. Словарь вида: {<название поля>: <текст>}.
        :param start_end_label: Надпись, показываемая перед временем начала и окончания события.
        :param time_separator: Разделитель между временем начала и временем конца.
        :param btn_show_details_label: Надпись на кнопке подробностей.
        """

        event = QEventWidget(title, time_start, time_end, wdg_description, time_separator, start_end_label,
                             btn_show_details_label)
        self.add_custom_event(event, id_, type_)

    def add_custom_event(self, event: QEventWidget, id_: int, type_: str):
        """
        Добавляет событие
        :param event: экземпляр QEventWidget.
        :param type_: Тип события.
        :param id_: ID события.
        """
        if type_ not in self._events:  # Обновление словаря событий
            self._events[type_] = {id_: event}
        else:
            self._events[type_][id_] = event

        self._get_fact_size()
        self._place_wdg_event(event, id_, type_)

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

        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Maximum)

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


class EventsTodayWidget(QWidget):

    def __init__(self, title: str = GuiLabels.events_today):
        super().__init__()
        main_layout = QVBoxLayout()
        lbl = QLabel(title)
        self._wdg_layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area_content = QWidget()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_area_content)
        scroll_area_content.setLayout(self._wdg_layout)

        main_layout.addWidget(lbl)
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

    def add_event(self, title: str, date_start: str, date_end: str, wdg_description: dict = None) -> QToolTipLabel:
        """Добавляет событие в виджет."""
        wdg = QToolTipLabel(f'{title} ({date_start} - {date_end})', wdg_description)
        self._wdg_layout.addWidget(wdg)
        return wdg


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

    def sth(type_: str, id_: int):
        print(type_, id_)

    from test.client_test.utils.window import setup_gui
    text = {
        'Описание': 'То-то и то-то',
        'Создатель': 'Такой-то',
        'Участвуют': 'Тот и этот'
    }

    widget = EventsTodayWidget()
    for i in range(0, 20, 2):
        widget.add_event(1, '', '1:1', {'1': 'DER'})

    setup_gui(widget)

