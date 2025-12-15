from PySide6.QtCore import Signal

from terv.src.gui.windows.windows import BaseView
from terv.models.base import Base
from terv.src.gui.main_view import MainWindow
from terv.src.requester.requester import Requester


class BaseViewHandler:
    """Базовый обработчик виджета. Использует одну модель из БД"""

    def __init__(self, window: BaseView, model: Base):
        self._window = window
        self._model = model

    def get_model(self) -> Base:
        return self._model

    def set_model(self, model: Base):
        self._model = model


class BaseWindowHandler:
    closed = Signal()

    def __init__(self, window: BaseView, main_view: MainWindow, requester: Requester):
        self._window = window
        self._main_view = main_view
        self._requester = requester

