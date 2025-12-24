from PySide6.QtWidgets import QWidget
from terv.src.gui.windows.windows import BaseView

import logging


logging.basicConfig(level=logging.DEBUG)
logging.debug('Module test\\client_test\\utils\\windows.py is running')


class WindowFirst(BaseView):

    def __init__(self):
        super().__init__()
        logging.debug('WindowFirst initialized')

    def close(self):
        logging.debug('WindowFirst closed')


class WindowSecond(BaseView):

    def __init__(self):
        super().__init__()
        logging.debug('WindowSecond initialized')

    def close(self):
        logging.debug('WindowSecond closed')


class WindowThird(BaseView):

    def __init__(self):
        super().__init__()
        logging.debug('WindowThird initialized')

    def close(self):
        logging.debug('WindowThird closed')


if __name__ == '__main__':
    from terv.main import launch, Logic, MainWindow

