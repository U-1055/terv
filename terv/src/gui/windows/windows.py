from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal

import logging


logging.basicConfig(level=logging.DEBUG)

logging.debug('Module windows.py is running')

class BaseView(QWidget):
    tried_to_return = Signal()  # Окно попытались свернуть
    tried_to_close = Signal()  # Окно попытались закрыть
    destroyed = Signal()  # Окно удалено

    def try_to_return(self):
        self.tried_to_return.emit()
    
    def destroy(self, /, destroyWindow = ..., destroySubWindows = ...):
        self.destroyed.emit()
        super().destroy(destroyWindow, destroySubWindows)


class PersonalTasksWindow(BaseView):

    def __init__(self):
        super().__init__()
        logging.debug('PersonalTaskWindow initialized')

    def close(self):
        super().close()
        logging.debug('PersonalTaskWindow closed')


class CalendarWindow(BaseView):

    def __init__(self):
        super().__init__()
        logging.debug('CalendarWindow initialized')

    def close(self):
        super().close()
        logging.debug('CalendarWindow closed')
