import time
from concurrent.futures import ThreadPoolExecutor
import typing as tp
import logging
import asyncio

logging.basicConfig(level=logging.DEBUG)
logging.debug('Module requester.py is running')


class Requester:
    """
    Класс для взаимодействия с API.
    """

    def __init__(self, server: str):
        self._server = server
        self._thread_pool = ThreadPoolExecutor()

    def _execute(self, func: tp.Callable, *args, **kwargs):
        thread = self._thread_pool.submit(func, *args, **kwargs)
        result = thread.result()

    def get_sth(self):
        logging.debug('Request has been taken')
        self._execute(time.sleep, 5)
        logging.debug('Request has been completed')

    def get_users(self):
        pass

    def get_workflows(self):
        pass

    def get_tasks(self):
        from terv.models.common_models import PersonalTask
        return (PersonalTask() for i in range(15))


    def update_workflows(self):
        pass

    def delete_workflows(self):
        pass

    def add_workflows(self):
        pass

    def register(self):
        pass

    def authorize_by_token(self):
        pass

    def authorize_by_password(self):
        pass


if __name__ == '__main__':
    pass
