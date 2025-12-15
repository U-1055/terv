from terv.src.gui.main_view import  MainWindow
from terv.src.requester.requester import Requester
from terv.utils.timeout_dict import TimeoutDict
from terv.utils.timeout_list import TimeoutList
from terv.src.src.handlers.userflow_handler import UserFlowWindowHandler
from terv.src.src.handlers.personal_tasks_handler import PersonalTasksWindowHandler


class Logic:
    """Главный класс логики приложения."""

    def __init__(
            self,
            view: MainWindow,
            model,
            requester: Requester,
            timeout: int
    ):
        self._view = view
        self._requester = requester
        self._view.btn_pressed.connect(self._requester.get_sth)

        self._win_handlers = TimeoutList(timeout)
        self._view.btn_open_userflow_pressed.connect(self._)

    def _update_state(self):
        self._requester.get_sth()
        self._requester.get_sth()
        self._requester.get_sth()

    def _open_personal_tasks_window(self):
        window = self._view.open_personal_tasks_window()
        win_handler = PersonalTasksWindowHandler(window, self._view, self._requester)
        win_handler.closed.connect(self._close_some_win())

    def _open_userflow(self):
        window = self._view.open_personal_tasks_window()
        win_handler = PersonalTasksWindowHandler(window, self._view, self._requester)

    def prepare_close_win(self):
        """Обрабатывает закрытие окна."""
        self._win_handlers.pop(-1)

    def _update_win(self):
        pass


if __name__ == '__main__':
    pass
