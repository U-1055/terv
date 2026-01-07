from PySide6.QtCore import QObject

from client.src.gui.widgets_view.base_view import BaseView
from client.models.common_models import Base


class BaseViewHandler(QObject):
    """Базовый обработчик виджета. Использует одну модель из БД"""

    def __init__(self, window: BaseView, model: Base = None):
        super().__init__()
        self._window = window
        self._model = model

    def get_model(self) -> Base:
        return self._model

    def set_model(self, model: Base):
        self._model = model

    def to_loading_state(self):
        pass

    def to_normal_state(self):
        pass


if __name__ == '__main__':
    pass
