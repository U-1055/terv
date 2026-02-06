from PySide6.QtCore import QTimer, Qt

import dataclasses
import datetime
import logging
import threading

from client.src.src.handlers.window_handlers.base import BaseWindowHandler, MainWindow, Requester, Model, RequestsGroup
from client.src.base import DataStructConst, widgets_labels, labels_widgets, GuiLabels
from client.src.src.handlers.widgets_view_handlers.userflow_handlers import TaskViewHandler
from client.src.gui.windows.userflow_window import UserFlowWindow
from client.src.gui.widgets_view.userflow_view import (TaskWidgetView, ScheduleWidgetView, NotesWidgetView,
                                                       WidgetSettingsMenu)
from client.src.src.handlers.widgets_view_handlers.userflow_handlers import (NotesViewHandler, ScheduleViewHandler,
                                                                             ReminderViewHandler)
import client.models.common_models as cm
from client.utils.data_tools import make_unique_dict_names
from common.base import DBFields, ObjectTypes, TasksStatuses
from client.src.gui.sub_widgets.widgets import QStructuredText
from client.utils.data_tools import iterable_to_str


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
        self._data_model: 'UserFlowDataModel' = UserFlowDataModel()
        self._task_widget: TaskWidgetView | None = None
        self._notes_view_handler: NotesWidgetView | None = None
        self._schedule_view_handler: ScheduleWidgetView | None = None
        self._window.btn_set_widgets_pressed.connect(self._on_btn_set_widgets_pressed)

        self._main_thread_id = threading.get_ident()

        self._timer = QTimer()

    def _on_btn_set_widgets_pressed(self):
        selected_widgets = []
        for widget in DataStructConst.names_widgets:  # Выбираем виджеты, у которых есть настройки
            if self._model.get_widget_settings(widget):
                selected_widgets.append(widgets_labels.get(widget))

        widgets = [widgets_labels.get(widget) for widget in DataStructConst.names_widgets]

        settings_window = WidgetSettingsMenu(widgets, selected_widgets)
        settings_window.set.connect(self._set_widgets_settings)
        self._main_view.show_dialog_window(settings_window, title=GuiLabels.widgets_settings_window, modality=False)

    def _on_reminder_edited(self, last_name: str, current_name: str):
        self._model.delete_reminder(last_name)
        self._model.add_reminder(current_name)

    def _on_reminder_completed(self, reminder: str):
        self._model.delete_reminder(reminder)

    def _on_reminder_added(self, reminder: str):
        self._model.add_reminder(reminder)

    def _on_id_clicked(self):
        pass

    def _on_task_completed(self, type_: str, id_: int):
        """Обрабатывает выполнение задачи в виджете задач."""
        access = self._model.get_access_token()
        if type_ == ObjectTypes.wf_task:
            request = self._requester.set_wf_task_status(id_, TasksStatuses.completed, access)
        elif type_ == ObjectTypes.personal_task:
            request = self._requester.set_personal_task_status(id_, TasksStatuses.completed, access)
        else:
            return

        request.finished.connect(lambda request_: self._prepare_request(request_))

    def _set_widgets_settings(self, widgets: tuple[str, ...]):
        """Устанавливает настройки виджетов (Изменяет список отображаемых виджетов)."""
        widgets = [labels_widgets[widget] for widget in widgets]  # Надписи виджетов переводим в их названия
        for widget in DataStructConst.names_widgets:
            if widget not in widgets:
                self._model.delete_widget_settings(widget)

        for widget in widgets:
            self._model.put_widget_settings(widget, 0, 0, 1, 1)

        self._place_settable_widgets()  # Обновляем конфигурацию

    def _set_user(self, user_info: tuple[dict]):
        self._data_model.user = cm.User(**user_info[0])

    def _set_tasks_widget(self):
        """Обрабатывает данные для виджета задач."""

        tasks = [*self._data_model.wf_tasks, *self._data_model.personal_tasks]
        if not self._task_widget:
            return

        for task in tasks:

            plan_deadline = task.plan_deadline.date().strftime(DataStructConst.gui_date_format)

            if task.__tablename__ == ObjectTypes.wf_task:
                task: cm.WFTask
                description = {GuiLabels.title: task.name, GuiLabels.description: task.description,
                               GuiLabels.workflow: f'#{task.workflow_id}', GuiLabels.plan_deadline: plan_deadline}
                if task.project_id:
                    description.update({GuiLabels.project: f'#{task.project_id}'})
                if task.responsible:
                    description.update({GuiLabels.responsible: iterable_to_str(task.responsible, ',', '#')})

            elif task.__tablename__ == ObjectTypes.personal_task:
                task: cm.PersonalTask
                description = {GuiLabels.title: task.name, GuiLabels.description: task.description,
                               GuiLabels.plan_deadline: plan_deadline}
            else:
                continue

            if task.plan_start_work_date:
                plan_start_work_date = task.plan_start_work_date.date().strftime(DataStructConst.gui_date_format)
                description.update({GuiLabels.plan_start_work_date: plan_start_work_date})
            if task.fact_start_work_date:
                fact_start_work_date = task.fact_start_work_date.date().strftime(DataStructConst.gui_date_format)
                description.update({GuiLabels.fact_start_work_date: fact_start_work_date})

            # ToDo: подвязка на нажатие на ID'ы в QStructuredText
            self._task_widget.add_task(task.name, task.id, task.__tablename__, description)

    def _place_settable_widgets(self):
        self._window.delete_notes_widget()
        self._window.delete_tasks_widget()
        self._window.delete_reminder_widget()
        self._window.delete_schedule_widget()

        for widget_type in self._data_const.names_widgets:
            result = self._model.get_widget_settings(widget_type)
            if not result:
                continue

            x, y, x_size, y_size = (result.get(self._data_const.x), result.get(self._data_const.y),
                                    result.get(self._data_const.x_size), result.get(self._data_const.y_size))

            if widget_type == self._data_const.tasks_widget:
                self._task_widget = self._window.place_task_widget(x, y, x_size, y_size)
                self._task_widget.task_completed.connect(self._on_task_completed)
                self._get_task_handler_data()
                logging.debug('Tasks widget placed.')
            if widget_type == self._data_const.notes_widget:
                widget_view = self._window.place_notes_widget(x, y, x_size, y_size)
                note = self._model.get_note()
                handler = NotesViewHandler(widget_view)
                handler.set_notes(note)
                logging.debug('Notes widget placed')
            if widget_type == self._data_const.schedule_widget:
                widget_view = self._window.place_schedule_widget()
                self._schedule_view_handler = widget_view
                self._get_schedule_widget_data()
                logging.debug('Schedule widget placed')
            if widget_type == self._data_const.reminder_widget:
                reminders = self._model.get_reminders()
                widget_view = self._window.place_reminder_widget(x, y, x_size, y_size)
                handler = ReminderViewHandler(widget_view)
                handler.set_max_reminder_length(DataStructConst.max_reminder_length)
                handler.set_reminders(reminders)
                handler.reminder_completed.connect(self._on_reminder_completed)
                handler.reminder_added.connect(self._on_reminder_added)
                handler.reminder_edited.connect(self._on_reminder_edited)
                logging.debug('Reminder widget placed')

    def _get_user_info(self):
        request = self._requester.get_user_info(self._model.get_access_token())
        request.finished.connect(lambda response: self._prepare_request(response, self._set_user))

    def update_state(self):
        self._get_user_info()
        self._place_settable_widgets()

    def update_data(self):
        self._get_task_handler_data()

    def _set_personal_daily_events(self, events: tuple[dict, ...] ):
        self._data_model.personal_daily_events = [cm.PersonalDailyEvent(**event) for event in events]

    def _set_personal_many_days_events(self, events: tuple[dict, ...]):
        self._data_model.personal_many_days_events = [cm.PersonalManyDaysEvent(**event) for event in events]

    def _set_wf_many_days_events(self, events: tuple[dict, ...]):
        self._data_model.wf_many_days_events = [cm.WFManyDaysEvent(**event) for event in events]

    def _set_wf_daily_events(self, events: tuple[dict, ...]):
        self._data_model.wf_daily_events = [cm.WFDailyEvent(**event) for event in events]

    def _set_schedule_widget(self):
        events = [*self._data_model.wf_daily_events, *self._data_model.personal_daily_events,
                  *self._data_model.wf_many_days_events, *self._data_model.personal_many_days_events]
        event_views_data = []
        for event in events:
            time_start = event.time_start.strftime('%H:%M')
            time_end = event.time_end.strftime('%H:%M')

            if event.__tablename__ == ObjectTypes.wf_daily_event:
                event: cm.PersonalDailyEvent
                structured_data = {}
                description = QStructuredText()

            if event.__tablename__ == ObjectTypes.personal_daily_event:
                event: cm.WFDailyEvent

            self._schedule_view_handler.add_event(event.name, time_start, time_end)

    def _set_personal_tasks(self, tasks: tuple[dict, ...]):
        self._data_model.personal_tasks = [cm.PersonalTask(**task) for task in tasks]

    def _set_wf_tasks(self, tasks: tuple[dict, ...]):
        self._data_model.wf_tasks = [cm.WFTask(**task) for task in tasks]

    def _get_schedule_widget_data(self):
        """Настраивает виджет расписания."""
        access_token = self._model.get_access_token()

        if self._data_model.user:
            personal_daily_events = self._requester.get_personal_daily_events(self._data_model.user.id, access_token,
                                                                              datetime.date.today())
            personal_daily_events.finished.connect(lambda request: self._prepare_request(request, self._set_personal_daily_events))
            personal_many_days_events = self._requester.get_personal_many_days_events(self._data_model.user.id, access_token,
                                                                                      datetime.date.today())
            personal_many_days_events.finished.connect(lambda request: self._prepare_request(request, self._set_personal_many_days_events))

            wf_daily_events = self._requester.get_wf_daily_events_by_users(self._data_model.user.id,
                                                                           self._data_model.user.notified_daily_events,
                                                                           access_token,
                                                                           datetime.date.today(),
                                                                           )
            wf_daily_events.finished.connect(lambda request: self._prepare_request(request, self._set_wf_daily_events))

            wf_many_days_events = self._requester.get_wf_many_days_events_by_user(
                self._data_model.user.id,
                self._data_model.user.notified_many_days_events,
                access_token,
                datetime.date.today(),
                    )
            wf_many_days_events.finished.connect(lambda request: self._prepare_request(request, self._set_wf_many_days_events))

            group = self._requester.create_group(personal_daily_events, personal_many_days_events, wf_daily_events,
                                                 wf_many_days_events)
            group.finished.connect(lambda request: self._set_schedule_widget())

        else:
            self._get_user_info()

    def _get_task_handler_data(self):
        """Получает данные для обработчика задач и вызывает методы для его настройки."""
        access_token = self._model.get_access_token()

        # ToDo: описать два подхода к запросам (через группу и через последовательные подвязки на сигналы и подвязку на сигнал группы в конце)
        if self._data_model.user:
            personal_tasks = self._requester.get_personal_tasks(self._data_model.user.id, access_token, datetime.date.today())
            personal_tasks.finished.connect(lambda request_: self._prepare_request(request_, self._set_personal_tasks))
            wf_tasks = self._requester.get_wf_tasks_by_user(self._data_model.user.id, access_token, datetime.date.today())
            wf_tasks.finished.connect(lambda request_: self._prepare_request(request_, self._set_wf_tasks))

            group = self._requester.create_group(personal_tasks, wf_tasks)
            group.finished.connect(lambda _: self._set_tasks_widget())

        else:
            request = self._requester.get_user_info(access_token)
            request.finished.connect(lambda request_: self._prepare_request(request_, lambda _: self._get_task_handler_data()))


@dataclasses.dataclass
class UserFlowDataModel:
    """Датакласс для асинхронного взаимодействия с данными из UserFlowHandler."""

    personal_tasks: list[cm.PersonalTask] = ()
    wf_tasks: list[cm.WFTask] = ()
    user: cm.User | None = None
    personal_daily_events: list[cm.PersonalDailyEvent] = ()
    personal_many_days_events: list[cm.PersonalManyDaysEvent] = ()
    wf_daily_events: list[cm.WFDailyEvent] = ()
    wf_many_days_events: list[cm.WFManyDaysEvent] = ()
