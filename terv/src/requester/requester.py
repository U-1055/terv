import time
import typing as tp
import asyncio
import threading

import httpx


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
            await client.post(f'{self._server}/register', json={'login': login, 'password': password, 'email': email})


if __name__ == '__main__':
    pass

