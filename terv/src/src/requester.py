import time
import typing as tp
import asyncio


class Requester:

    def __init__(self, server: str):
        self._server = server
        self._running_event_loop = None

    @staticmethod
    def _prepare_request(func):
        def prepare(*args):
            loop = asyncio.get_event_loop()
            if not loop:
                loop = asyncio.new_event_loop()
            future = asyncio.run_coroutine_threadsafe(func(*args), loop)
            return future

        return prepare

    @_prepare_request
    async def get_sth(self, *args) -> str:
        await asyncio.sleep(5)
        return 'result'

    async def start_loop(self):
        while True:
            await asyncio.sleep(1)
            print(1)


class LogicImitator:

    def __init__(self, requester: Requester):
        self._requester = requester
        self.update_state()

    def update_state(self):
        print(self._requester.get_sth())

    def gui_process(self):
        while True:
            time.sleep(1)
            print('GUI is running')


async def main():
    requester = Requester('')
    task2 = asyncio.create_task(requester.get_sth())

    await task2

if __name__ == '__main__':
    requester = Requester('')
    logic = LogicImitator(requester)
    logic.gui_process()

