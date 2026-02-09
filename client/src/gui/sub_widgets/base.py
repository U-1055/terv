from PySide6.QtWidgets import QWidget, QStyle, QStyleOption
from PySide6.QtGui import QPainter


class BaseWidget(QWidget):
    """
    QWidget с переопределённым методом paintEvent. Предназначен для удобного использования стилей в программе.
    Хранит таблицу стилей как атрибут класса и имеет метод для её установки.
    """
    _style_sheet: str = ''

    def __init__(self):
        super().__init__()
        self.setStyleSheet(self._style_sheet)

    def to_loading_state(self):
        pass

    def to_normal_state(self):
        pass

    def paintEvent(self, event, /):
        super().paintEvent(event)
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter)

    @classmethod
    def set_class_style_sheet(cls, style_sheet: str):
        cls._style_sheet = style_sheet
