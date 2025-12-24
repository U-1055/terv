from PySide6.QtCore import QTimer

from terv.src.src.handlers.window_handlers.base import BaseWindowHandler, MainWindow, Requester, Model, BaseWindow
from terv.src.base import DataStructConst
from terv.src.gui.widgets_view.base_view import BaseView
from terv.src.src.handlers.widgets_view_handlers.userflow_handlers import TaskViewHandler
from terv.src.gui.windows.windows import UserFlowWindow
from terv.src.gui.widgets_view.userflow_view import TaskWidgetView

from terv.utils.data_tools import make_unique_dict_names


class UserFlowWindowHandler(BaseWindowHandler):

    def __init__(
            self,
            window: UserFlowWindow,
            main_view: MainWindow,
            requester: Requester,
            model: Model,
            data_const: DataStructConst = DataStructConst()
    ):
        super().__init__(window, main_view, requester, model)
        self._window, self._main_view, self._requester, self._model, self._data_const = window, main_view, requester, model, data_const
        self._task_view_handler: TaskViewHandler = None
        self._timer = QTimer()
        self._update_state()

    def _set_tasks(self, tasks: tuple[dict, ...]):
        if not self._task_view_handler:
            return

        dicts = []
        for task in tasks:
            dicts.append({task['name']: task['id']})
        tasks_list = make_unique_dict_names(dicts)
        self._task_view_handler.tasks = tasks_list

    def _update_state(self):
        for widget_type in self._data_const.names_widgets:
            result = self._model.get_widget_settings(widget_type)
            if widget_type == self._data_const.tasks_widget:
                widget_view = self._window.place_task_widget()
                self._set_task_handler(widget_view)

    def _set_task_handler(self, view: TaskWidgetView) -> TaskViewHandler:
        """Настраивает обработчик задач."""
        self._task_view_handler = TaskViewHandler(view, {'namer': int})
        tasks = self._requester.get_sth()
        self._timer.singleShot(1000 * 6, lambda: self._set_data_to_widget(tasks, self._set_tasks))
        return self._task_view_handler


def close(self):
    pass


class UserTasksWindowHandler(BaseWindowHandler):
    pass


