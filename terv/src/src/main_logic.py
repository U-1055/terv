from terv.src.gui.main_view import BaseWindow, MainWindow
from terv.src.requester.requester import Requester


class Logic:

    def __init__(self, view: MainWindow, model, requester: Requester):
        self._opened_now: BaseWindow
        self._view = view
        self._requester = requester
        self._view.btn_pressed.connect(self._requester.get_sth)

    def _update_state(self):
        self._requester.get_sth()
        self._requester.get_sth()
        self._requester.get_sth()

    def _open_some_win(self):
        pass

    def _close_some_win(self):
        pass

    def _update_some_win(self):
        pass


if __name__ == '__main__':
    pass
