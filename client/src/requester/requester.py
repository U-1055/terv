import httpx

import time
import typing as tp
import asyncio
import threading

import client.src.requester.errors as err


def run_loop(loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def synchronized_request(func):
    def prepare(*args) -> asyncio.Future:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            thread = threading.Thread(target=lambda: run_loop(loop))
            thread.start()
            time.sleep(0.1)

        future = asyncio.run_coroutine_threadsafe(func(*args), loop)
        return future

    return prepare


class Requester:

    def __init__(self, server: str):
        self._server = server
        self._running_event_loop = None

    @synchronized_request
    async def register(self, login: str, password: str, email: str):
        async with httpx.AsyncClient() as client:
            result = await client.post(f'{self._server}/register', json={'login': login, 'password': password, 'email': email})
        return result.json().get('content')

    @synchronized_request
    async def update_tokens(self, refresh_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            result = await client.post(f'{self._server}/auth/refresh', json={'refresh_token': refresh_token})

        if result.status_code == 400:
            raise err.ExpiredRefreshToken

        return result.json().get('content')

    @synchronized_request
    async def authorize(self, login: str, password: str) -> dict:
        async with httpx.AsyncClient() as client:
            result = await client.post(f'{self._server}/auth/login', json={'login': login, 'password': password})

        if result.status_code == 400:
            raise err.UnknownCredentials

        return result.json().get('content')

    @synchronized_request
    async def get_user_info(self, access_token: str):
        async with httpx.AsyncClient() as client:
            result = await client.get(f'{self._server}/users', headers={'Authorization': access_token})

        if result.status_code == 401:
            raise err.ExpiredAccessToken
        if result.status_code == 500:
            raise err.ServerError

        return result.json().get('content')

    @synchronized_request
    async def get_personal_tasks(self, user_id: int, access_token: str):
        async with httpx.AsyncClient() as client:
            result = await client.get(f'{self._server}/personal_tasks')

        if result.status_code == 401:
            raise err.ExpiredAccessToken
        if result.status_code == 500:
            raise err.ServerError

        return result.json().get('content')








if __name__ == '__main__':
    pass

