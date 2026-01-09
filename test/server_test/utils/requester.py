import httpx

from common.base import DataStruct


class TestRequester:

    def __init__(self, server: str, common_data_struct: DataStruct = DataStruct()):
        self._server = server
        self._common_ds = common_data_struct

    def authorize(self, login: str, password: str) -> httpx.Response:
        result = httpx.post(f'{self._server}/auth/login', json={self._common_ds.login: login, self._common_ds.password: password})
        return result

    def update_tokens(self, refresh_token: str) -> httpx.Response:
        result = httpx.post(f'{self._server}/auth/refresh', json={self._common_ds.refresh_token: refresh_token})
        return result

    def register(self, login: str, password: str, email: str) -> httpx.Response:
        result = httpx.post(f'{self._server}/register', json={self._common_ds.login: login, self._common_ds.email: email, self._common_ds.password: password})
        return result

    def get_user_info(self, access_token: str) -> httpx.Response:
        result = httpx.post(f'{self._server}/users', headers={'Authorization': access_token})
        return result
