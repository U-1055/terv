from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Signal

from client.src.gui.widgets_view.userspace_view import TaskWidgetView
from common.logger import config_logger, CLIENT
from client.src.base import LOG_DIR, MAX_FILE_SIZE, MAX_BACKUP_FILES, LOGGING_LEVEL

logger = config_logger(__name__, CLIENT, LOG_DIR, MAX_BACKUP_FILES, MAX_FILE_SIZE, LOGGING_LEVEL)


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
        logger.debug('Window destroyed')
        super().destroy(destroyWindow, destroySubWindows)


class PersonalTasksWindow(BaseWindow):

    def __init__(self):
        super().__init__()
        
        logger.debug('PersonalTaskWindow initialized')

    def close(self):
        super().close()
        logger.debug('PersonalTaskWindow closed')

    def update(self):
        pass


class CalendarWindow(BaseWindow):

    def __init__(self):
        super().__init__()
        logger.debug('CalendarWindow initialized')

    def close(self):
        super().close()
        logger.debug('CalendarWindow closed')


if __name__ == '__main__':
    pass
