from PySide6.QtCore import Signal, QObject

from terv.src.gui.windows.windows import BaseView
from terv.models.base import Base
from terv.src.gui.main_view import MainWindow
from terv.src.requester.requester import Requester


class BaseViewHandler(QObject):
    """Базовый обработчик виджета. Использует одну модель из БД"""

    def __init__(self, window: BaseView, model: Base):
        super().__init__()
        self._window = window
        self._model = model

    def get_model(self) -> Base:
        return self._model

    def set_model(self, model: Base):
        self._model = model


class BaseWindowHandler(QObject):
    closed = Signal()

    def __init__(self, window: BaseView, main_view: MainWindow, requester: Requester):
        super().__init__()
        self._window = window
        self._main_view = main_view
        self._requester = requester

    def get_window(self):
        return self._window

    def close(self):
        self._window.close()
        self.closed.emit()

