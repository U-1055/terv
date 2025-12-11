import time


class Requester:

    def __init__(self, server: str):
        self._server = server

    def get_sth(self, *args) -> str:
        time.sleep(10)
        return 'result'


