"""Обобщённые Qt-подобные виджеты."""
import logging

from PySide6.QtWidgets import (QWidget, QGridLayout, QLabel, QScrollArea, QVBoxLayout, QSizePolicy, QMenu, QWidgetAction,
                               QProgressBar)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont, QCursor
from PySide6.QtCore import Qt, QPoint, QThread, QObject, QTimer

import typing as tp

from client.src.base import GUIStyles
from client.src.gui.sub_widgets.util_widgets import QClickableLabel

logging.basicConfig(level=logging.DEBUG)


class QStructuredText(QWidget):
    """
    Виджет, представляющий собой структурированный по полям текст. Структура преобразуется из словаря (Ключи будут
    названиями полей, значения - их содержимым).

    :var content_clicked: Сигнал, испускаемый при нажатии на содержимое поля. Передаёт название поля и экземпляр
                          QStructuredText.
    :var field_clicked: Сигнал, испускаемый при нажатии на поле. Передаёт название поля и экземпляр
                        QStructuredText.

    :param structure: словарь, по которому будет создана структура виджета (ключи - поля, значения - содержимое полей).
    :param field_font: шрифт текста полей.
    :param content_font: шрифт текста содержимого.
    :param fields_alignment: выравнивание полей (AlignmentFlag).
    :param content_alignment: выравнивание содержимого (AlignmentFlag).
    :param field_suffix: окончание, добавляемое к названиям полей. По умолчанию отсутствует.

    """
    content_clicked = Signal(str, tp.Any)  # Сигнал, вызываемый при нажатии на поле. Передаёт название поля
    field_clicked = Signal(str, tp.Any)  # Сигнал, вызываемый при нажатии на поле. Передаёт название поля

    field_column = 0  # Столбцы, в которых размещаются виджеты
    content_column = 1

    def __init__(self, structure: dict = None, field_font: QFont = GUIStyles.bold_font,
                 content_font: QFont = GUIStyles.base_font, fields_alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
                 content_alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft, field_suffix: str = ''):
        super().__init__()
        if structure:
            self._structure = {key: str(structure[key]) for key in structure}
        else:
            self._structure = dict()

        self._field_font = field_font
        self._content_font = content_font
        self._field_align = fields_alignment
        self._content_align = content_alignment
        self._labels_size_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._field_suffix = field_suffix

        self._tooltip_fields = {}

        main_layout = QVBoxLayout()
        main_layout.setSizeConstraint(QGridLayout.SizeConstraint.SetFixedSize)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area_content = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_area_content)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._layout = QGridLayout()
        scroll_area_content.setLayout(self._layout)

        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
        self._place_fields()

    def _place_field(self, field: str, content: str, row: int):
        lbl_field = QToolTipLabel(field, alignment=self._field_align)
        lbl_field.setFont(self._field_font)
        lbl_field.setSizePolicy(self._labels_size_policy)
        lbl_field.clicked.connect(lambda: self.click_field(field))

        lbl_content = QToolTipLabel(content, wordWrap=True, alignment=self._content_align)
        lbl_content.setFont(self._content_font)
        lbl_content.setSizePolicy(self._labels_size_policy)
        lbl_content.clicked.connect(lambda: self.click_content(field))

        self._layout.addWidget(lbl_field, row, self.field_column)
        self._layout.addWidget(lbl_content, row, self.content_column)

    def _place_fields(self):
        row = 0
        for key in self._structure:
            self._place_field(key, self._structure[key], row)
            row += 1

    def _replace_fields(self):
        structure = self._structure
        self.clear()
        self._structure = structure
        self._place_fields()

    def click_field(self, field: str):
        self.field_clicked.emit(field, self)

    def click_content(self, field: str):
        self.content_clicked.emit(field, self)

    def delete_field(self, field: str):
        self._structure.pop(field)
        self._place_fields()

    def put_field(self, field: str, content: str):
        """Обновляет содержимое поля (Перезаписывает его значение). Если поля нет - оно будет создано."""
        self._structure[field] = content
        self._place_fields()

    def put_fields(self, structure: dict):
        """Обновляет виджет полями из переданного словаря (аналогично dict.update())."""
        self._structure.update(structure)
        self._place_fields()

    def content(self, field: str) -> str | None:
        """Возвращает содержимое поля field."""
        return self._structure.get(field)

    def fields(self) -> tuple[str, ...]:
        """Возвращает все поля виджета."""
        return tuple(self._structure.keys())

    def clear(self):
        """Удаляет все поля."""
        self._structure = dict()
        self._place_fields()

    def structure(self) -> dict:
        """Возвращает структуру текста в виде: {<поле>: <текст поля>}."""
        return self._structure

    def set_structure(self, structure: dict):
        self._structure = structure
        self._place_fields()

    def set_field_font(self, font: QFont):
        self._field_font = font
        self._replace_fields()

    def set_content_font(self, font: QFont):
        self._content_font = font
        self._replace_fields()

    def field_font(self) -> QFont:
        return self._field_font

    def content_font(self) -> QFont:
        return self._content_font

    def set_field_alignment(self, field_alignment: Qt.AlignmentFlag):
        self._field_align = field_alignment
        self._replace_fields()

    def set_content_alignment(self, content_alignment: Qt.AlignmentFlag):
        self._content_align = content_alignment
        self._replace_fields()

    def field_alignment(self) -> Qt.AlignmentFlag:
        return self._field_align

    def content_alignment(self) -> Qt.AlignmentFlag:
        return self._content_align

    def set_field_suffix(self, field_suffix: str):
        self._field_suffix = field_suffix

    def field_suffix(self) -> str:
        return self._field_suffix

    def show_structured_tooltip(self, field: str, tooltip: dict, on_field: bool = True):
        menu = QMenu()
        wdg_action = QWidgetAction(menu)
        menu.setStyleSheet(self.styleSheet())
        wdg_structured_text = QStructuredText(tooltip)
        wdg_structured_text.setStyleSheet(self.styleSheet())
        wdg_action.setDefaultWidget(wdg_structured_text)
        menu.addAction(wdg_action)

        for i in range(self._layout.rowCount()):
            widget = self._layout.itemAtPosition(i, self.field_column).widget()
            logging.warning(f'Iter: {i}. Text: {widget.text()}. Field: {field}')
            if isinstance(widget, QLabel) and widget.text() == field:
                menu.exec(QCursor.pos())
                logging.warning(f'Menu placed by coordinates: {QCursor.pos()}')


class QToolTipLabel(QClickableLabel):
    """
    QLabel, по нажатию на который выводится QStructuredText.

    :var tooltip_field_clicked: Сигнал, вызывающийся при нажатии на поле подсказки виджета. Передаёт название поля.
    :var tooltip_content_clicked: Сигнал, вызывающийся при нажатии на текст поля подсказки виджета. Передаёт название поля.

    """

    tooltip_field_clicked = Signal(str, tp.Any)
    tooltip_content_clicked = Signal(str, tp.Any)

    def __init__(self, text: str = '', structured_text: dict | None = None, wordWrap: bool = False,
                 alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignHCenter):
        super().__init__(text, alignment=alignment, wordWrap=wordWrap)
        self._structured_text = structured_text
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu_requested)

    def _on_tooltip_content_clicked(self, field: str, wdg: QStructuredText):
        self.tooltip_content_clicked.emit(field, wdg)

    def _on_context_menu_requested(self, pos: QPoint):
        if not self._structured_text:
            return

        menu = QMenu()
        action = QWidgetAction(menu)
        wdg_structured_text = QStructuredText(self._structured_text)
        wdg_structured_text.content_clicked.connect(self._on_tooltip_content_clicked)
        wdg_structured_text.setStyleSheet(self.styleSheet())
        menu.setStyleSheet(self.styleSheet())
        action.setDefaultWidget(wdg_structured_text)
        menu.addAction(action)
        menu.exec(self.mapToGlobal(pos))

    def structured_text(self) -> dict | None:
        return self._structured_text

    def set_structured_text(self, structured_text: dict | None):
        if structured_text is not None:
            self._structured_text = QStructuredText(structured_text)
        else:
            self._structured_text = None


class QProgressWidget(QWidget):
    """
    Виджет обновления прогресса.

    :var finished: Сигнал, испускаемый после достижения макс. значения прогресс-бара.

    :param text: Текст, показываемый во время работы прогресс-бара.
    :param minimum: Начальное значение.
    :param maximum: Конечное значение.
    :param interval: Шаг значения.
    :param time_interval: Время (в мс) между изменением значения.
    :param show_text: Показывать процентные значения прогресс-бара?
    :param ready_text: Текст, выводимый после достижения максимального значения прогресс-бара.

    """

    finished = Signal()

    def __init__(self, text: str | None = None, minimum: int | None = None, maximum: int | None = None,
                 interval: int | None = None, time_interval: int = 0, show_text: bool = True, ready_text: str = '',
                 text_font: QFont | None = None):
        super().__init__()
        self._is_running = False
        self._worker = ProgressWorker(minimum, maximum, interval, time_interval)
        self._worker.updated.connect(self._on_updated)
        self._worker.finished.connect(self._on_finished)
        self._ready_text = ready_text

        main_layout = QVBoxLayout()
        self._lbl_text = QLabel(text=text, wordWrap=True)
        if text_font:
            self._lbl_text.setFont(text_font)
        self._progress_bar = QProgressBar(self)
        self._progress_bar.setTextVisible(show_text)
        if not minimum:
            minimum = 0
        if not maximum:
            maximum = 100
        self._progress_bar.setMinimum(minimum)
        self._progress_bar.setMaximum(maximum)
        self._progress_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        main_layout.addWidget(self._progress_bar, alignment=Qt.AlignmentFlag.AlignVCenter)
        main_layout.addWidget(self._lbl_text, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self._progress_bar.setRange(minimum, maximum)
        self._progress_bar.setValue(0)
        self.setLayout(main_layout)
        self._worker.cycle()

    def _on_finished(self):
        if self._ready_text:
            self._lbl_text.setText(self._ready_text)
        self.finished.emit()

    def _on_updated(self, value: int):
        self._progress_bar.setValue(value)

    def start(self):
        """Запускает прогресс-бар."""
        self._worker.start()

    def stop(self):
        """Останавливает прогресс-бар."""
        self._worker.stop()

    def set_time_interval(self, time_interval: int):
        """Устанавливает временной интервал (в мс) между изменениями значений."""
        self._worker.set_interval(time_interval)

    def time_interval(self) -> int:
        return self._worker.time_interval()

    def interval(self) -> int:
        return self._worker.interval()

    def set_interval(self, interval: int):
        self._worker.set_interval(interval)

    def text(self) -> str:
        return self._lbl_text.text()

    def set_text(self, text: str):
        self._lbl_text.setText(text)

    def text_font(self) -> QFont:
        return self._lbl_text.font()

    def set_text_font(self, font: QFont):
        self._lbl_text.setFont(font)


class ProgressWorker(QObject):
    """
    Обработчик прогресс-бара.

    :var updated: Сигнал, испускаемый при обновлении значения прогресс-бара.
    :var finished: Сигнал, испускаемый при достижнии максимального значения прогресс-бара.

    :param minimum: Начальное значение.
    :param maximum: Конечное значение.
    :param interval: Шаг значения.
    :param time_interval: Время (в мс) между изменением значения.

    """
    updated = Signal(int)
    finished = Signal()

    def __init__(self, minimum: int | None = None, maximum: int | None = None, interval: int | None = None,
                 time_interval: int = 0):
        super().__init__()
        self._is_running = False
        if not minimum:
            minimum = 0
        if not maximum:
            maximum = 100
        if not interval:
            interval = 1
        self._value = minimum
        self._minimum = minimum
        self._maximum = maximum
        self._interval = interval
        self._time_interval = time_interval

    def cycle(self):
        if self._is_running:
            self._value += self._interval
            self.updated.emit(self._value)
        if self._value < self._maximum:
            QTimer.singleShot(self._time_interval, self.cycle)
        else:
            self.finished.emit()

    def value(self) -> int:
        return self._value

    def time_interval(self) -> int:
        return self._time_interval

    def set_time_interval(self, time_interval: int):
        """Устанавливает временной интервал (в мс) между изменениями значения прогресс-бара."""
        self._time_interval = time_interval

    def interval(self) -> int:
        return self._interval

    def set_interval(self, interval: int):
        self._interval = interval

    def start(self):
        self._is_running = True

    def stop(self):
        self._is_running = False


if __name__ == '__main__':
    from test.client_test.utils.window import setup_gui

    wdg = QStructuredText({'field#1': '13241434234234'})
    QTimer.singleShot(3000, lambda: wdg.show_structured_tooltip('field#1', {'TOOLTIP': "ASTR"}))
    setup_gui(wdg)
