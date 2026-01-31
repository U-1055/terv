"""Вспомогательные виджеты."""
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QLabel, QLineEdit
from PySide6.QtGui import QKeyEvent


class QClickableLabel(QLabel):
    """QLabel с сигналом clicked, вызываемым при нажатии ЛКМ на виджет."""

    clicked = Signal()

    def mousePressEvent(self, ev, /):
        self.clicked.emit()


class QMouseActivatingLineEdit(QLineEdit):
    """QLineEdit, который разрешает редактирование при нажатии мыши и запрещает при нажатии Enter."""

    def __init__(self, text: str = '', max_length: int = 20):
        super().__init__(text, maxLength=max_length)

    def mouseReleaseEvent(self, arg__1, /):
        self.setReadOnly(False)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return:
            self.setReadOnly(True)
            self.clearFocus()
        super().keyPressEvent(event)
