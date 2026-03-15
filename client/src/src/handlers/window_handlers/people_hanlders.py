"""Обработчик окна раздела "Люди"."""
from client.src.src.handlers.window_handlers.base import BaseWindowHandler


class PeopleWindowHandler(BaseWindowHandler):

    def __init__(self, window):
        super().__init__()