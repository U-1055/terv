from terv.src.gui.main_view import  MainWindow
from terv.src.requester.requester import Requester
from terv.utils.timeout_dict import TimeoutDict
from terv.utils.timeout_list import TimeoutList
from terv.src.src.handlers.userflow_handler import UserFlowWindowHandler
from terv.src.src.handlers.personal_tasks_handler import PersonalTasksWindowHandler
from terv.src.src.handlers.base import BaseWindowHandler


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

        self._win_handlers = TimeoutList(timeout, self._close_outdated_window, 15)
        self._view.btn_open_userflow_pressed.connect(self._open_userflow)
        self._view.btn_open_personal_tasks_window_pressed.connect(self._open_personal_tasks_window)

    def _update_state(self):
        self._requester.get_sth()
        self._requester.get_sth()
        self._requester.get_sth()

    def _close_outdated_window(self, handler: BaseWindowHandler):
        handler.close()

    def _get_last_handler(self, type_) -> BaseWindowHandler | None:
        for handler in self._win_handlers:
            if isinstance(handler, type_):
                return handler

    def _open_personal_tasks_window(self):
        self._win_handlers.update()

        current_window = self._get_last_handler(PersonalTasksWindowHandler)
        if current_window:
            self._view.open_window(current_window.get_window())
        else:
            window = self._view.open_personal_tasks_window()
            win_handler = PersonalTasksWindowHandler(window, self._view, self._requester)
            self._win_handlers.append(win_handler)

    def _open_userflow(self):
        self._win_handlers.update()

        current_window = self._get_last_handler(UserFlowWindowHandler)
        if current_window:
            self._view.open_window(current_window.get_window())
        else:
            window = self._view.open_personal_tasks_window()
            win_handler = UserFlowWindowHandler(window, self._view, self._requester)
            self._win_handlers.append(win_handler)

    def _update_win(self):
        pass


if __name__ == '__main__':
    pass
