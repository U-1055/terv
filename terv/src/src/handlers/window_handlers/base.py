import asyncio

from PySide6.QtCore import Signal, QObject

import typing as tp

from terv.src.gui.windows.windows import BaseWindow
from terv.models.base import Base
from terv.src.gui.main_view import MainWindow
from terv.src.requester.requester import Requester
from terv.src.client_model.model import Model


class BaseWindowHandler(QObject):
    closed = Signal()
    error_occurred = Signal(str, str)  # Произошла ошибка

    def __init__(self, window: BaseWindow, main_view: MainWindow, requester: Requester, model: Model):
        super().__init__()
        self._window = window
        self._main_view = main_view
        self._requester = requester
        self._model = model

    def _send_error(self, title: str, message: str):
        self.error_occurred.emit(title, message)

    def _set_data_to_widget(self, task: asyncio.Future, prepare_data_func: tp.Callable):
        """
        Обрабатывает передачу данных из асинхронного запроса в метод. Если данных не получено - выводит ошибку.
        :param task:
        :param prepare_data_func:
        :return:
        """
        result = task.result()
        if result:
            prepare_data_func(result)
        else:
            self._send_error('Timeout error', 'The data has not been received')

    def update_data(self):
        """
        Обновляет данные в обработчике. При вызове обработчик собирает данные со своих виджетов, делает соответствующие
        запросы на сервер, затем обновляет данных в виджетах.
        """
        pass

    def get_window(self):
        return self._window

    def close(self):
        self._window.close()
        self.closed.emit()

