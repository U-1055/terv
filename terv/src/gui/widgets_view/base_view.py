from PySide6.QtWidgets import QWidget


class BaseView(QWidget):

    def __init__(self):
        super().__init__()

    def to_loading_state(self):
        pass

    def to_normal_state(self):
        pass

