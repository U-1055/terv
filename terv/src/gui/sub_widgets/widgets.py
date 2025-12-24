from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout
from PySide6.QtCore import Signal


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


if __name__ == '__main__':
    pass

