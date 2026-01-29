from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QLineEdit
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QKeyEvent


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


class QMouseActivatingLineEdit(QLineEdit):
    """QLineEdit, который разрешает редактирование при нажатии мыши и запрещает при нажатии Enter."""

    def __init__(self, text: str = ''):
        super().__init__(text)

    def mouseReleaseEvent(self, arg__1, /):
        self.setReadOnly(False)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return:
            self.setReadOnly(True)
            self.clearFocus()
        super().keyPressEvent(event)


class Reminder(QWidget):
    """Виджет напоминания."""

    completed = Signal(QWidget)  # Напоминание закрыто. Возвращается виджет
    edited = Signal(str, str)  # Название редактировано. Первая строка - старое название, вторая - новое

    def __init__(self, label: str):
        super().__init__()
        self.name = label
        self._main_layout = QHBoxLayout()
        self._line_edit_lbl = QMouseActivatingLineEdit(label)
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


if __name__ == '__main__':
    pass

