"""Модель клиента для тестов сервера"""


class Model:

    def __init__(self):
        self._storage = {
            'refresh': '',
            'access': ''
        }

    def set_access_token(self, token_: str):
        self._storage['access'] = token_

    def set_refresh_token(self, token_: str):
        self._storage['refresh'] = token_

    def get_access_token(self) -> str:
        return self._storage.get('access')

    def get_refresh_token(self) -> str:
        return self._storage.get('refresh')

