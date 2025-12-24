from PySide6.QtCore import QObject

from terv.src.gui.widgets_view.base_view import BaseView
from terv.models.common_models import Base


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


if __name__ == '__main__':
    pass
