import asyncio
import logging
import pathlib

from client.src.src.handlers.window_handlers.base import BaseWindowHandler
from client.src.requester.requester import Requester
from client.src.client_model.model import Model


logging.basicConfig(level=logging.DEBUG)


class TestLogic(BaseWindowHandler):

    def _prepare_request(self, future: asyncio.Future):
        try:
            future.result()
        except BaseException as e:
            pass

    def register(self):
        future: asyncio.Future = self._requester.register()
        future.add_done_callback(lambda f: self._prepare_request(f))


class TestModel(Model):

    def __init__(self, path: pathlib.Path):
        super().__init__(path, path)
        self.access_token = None
        self.refresh_token = None

    def get_access_token(self) -> str:
        logging.debug('Access token returning')


if __name__ == '__main__':
    requester = Requester('localhost:5000')
    logic = TestLogic(None, None, requester, TestModel(pathlib.Path('')))
