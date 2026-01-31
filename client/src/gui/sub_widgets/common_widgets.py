"""Обобщённые Qt-подобные виджеты."""
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QScrollArea, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

import typing as tp

from client.src.base import GUIStyles
from client.utils.qt_utils import filled_rows_count
from client.src.gui.sub_widgets.util_widgets import QClickableLabel


class QStructuredText(QWidget):
    """
    Виджет, представляющий собой структурированный по полям текст. Структура преобразуется из словаря (Ключи будут
    названиями полей, значения - их содержимым).

    :param structure: словарь, по которому будет создана структура виджета (ключи - поля, значения - содержимое полей).
    :param field_font: шрифт текста полей.
    :param content_font: шрифт текста содержимого.
    :param fields_alignment: выравнивание полей (AlignmentFlag).
    :param content_alignment: выравнивание содержимого (AlignmentFlag).
    :param field_suffix: окончание, добавляемое к названиям полей. По умолчанию отсутствует.

    """

    content_clicked = Signal(str)  # Сигнал, вызываемый при нажатии на поле. Передаёт название поля
    field_clicked = Signal(str)  # Сигнал, вызываемый при нажатии на поле. Передаёт название поля

    field_column = 0  #  Столбцы, в которых размещаются виджеты
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
        lbl_field = QClickableLabel(field, alignment=self._field_align)
        lbl_field.setFont(self._field_font)
        lbl_field.setSizePolicy(self._labels_size_policy)
        lbl_field.clicked.connect(lambda: self.click_field(field))

        lbl_content = QClickableLabel(content, wordWrap=True, alignment=self._content_align)
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
        self.field_clicked.emit(field)

    def click_content(self, field: str):
        self.field_clicked.emit(field)

    def delete_field(self, field: str):
        self._structure.pop(field)
        self._place_fields()

    def put_field(self, field: str, content: str):
        """Обновляет содержимое поля (Перезаписывает его значение). Если поля нет - оно будет создано."""
        self._structure[field] = content
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


if __name__ == '__main__':
    from test.client_test.utils.window import setup_gui
    test_data = {
        'Описание': ''.join([f"{''.join(['C' for i in range(10)])} " for i1 in range(90)])
    }
    wdg = QStructuredText(test_data)
    wdg.field_clicked.connect(print)
    wdg.content_clicked.connect(print)

    setup_gui(wdg)
