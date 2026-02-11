from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Signal

import logging

from client.src.gui.widgets_view.userspace_view import TaskWidgetView

logging.basicConfig(level=logging.DEBUG)

logging.debug('Module windows.py is running')


class BaseWindow(QWidget):
    tried_to_return = Signal()  # Окно попытались свернуть
    tried_to_close = Signal()  # Окно попытались закрыть
    destroyed = Signal()  # Окно удалено

    def try_to_close(self):
        self.tried_to_close.emit()

    def try_to_return(self):
        self.tried_to_return.emit()
    
    def destroy(self, /, destroyWindow = ..., destroySubWindows = ...):
        self.destroyed.emit()
        logging.debug('Window destroyed')
        super().destroy(destroyWindow, destroySubWindows)


class PersonalTasksWindow(BaseWindow):

    def __init__(self):
        super().__init__()
        
        logging.debug('PersonalTaskWindow initialized')

    def close(self):
        super().close()
        logging.debug('PersonalTaskWindow closed')

    def update(self):
        pass


class CalendarWindow(BaseWindow):

    def __init__(self):
        super().__init__()
        logging.debug('CalendarWindow initialized')

    def close(self):
        super().close()
        logging.debug('CalendarWindow closed')


if __name__ == '__main__':
    pass
