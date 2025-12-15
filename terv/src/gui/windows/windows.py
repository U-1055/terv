from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal


class BaseView(QWidget):
    tried_to_return = Signal()  # Окно попытались свернуть

    def try_to_return(self):
        self.tried_to_return.emit()


class PersonalTasksWindow(BaseView):
    pass


class CalendarWindow(BaseView):
    pass

