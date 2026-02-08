from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor

import dataclasses
import datetime
import logging
import threading

from client.src.src.handlers.window_handlers.base import (BaseWindowHandler, MainWindow, Requester, Model, Request)
from client.src.base import DataStructConst, widgets_labels, labels_widgets, GuiLabels
from client.src.gui.windows.userflow_window import UserFlowWindow
from client.src.gui.widgets_view.userflow_view import (TaskWidgetView, ScheduleWidgetView, NotesWidgetView,
                                                       WidgetSettingsMenu)
from client.src.src.handlers.widgets_view_handlers.userflow_handlers import (NotesViewHandler, ReminderViewHandler)
import client.models.common_models as cm
from common.base import ObjectTypes, TasksStatuses
from client.utils.data_tools import iterable_to_str, get_lasting


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
        self._requests: 'UserFlowRequests' = UserFlowRequests()

        self._task_widget: TaskWidgetView | None = None
        self._notes_widget: NotesWidgetView | None = None
        self._schedule_widget: ScheduleWidgetView | None = None
        self._window.btn_set_widgets_pressed.connect(self._on_btn_set_widgets_pressed)

        self._main_thread_id = threading.get_ident()

        self._timer = QTimer()

    def _on_note_changed(self):
        note = self._notes_widget.notes()
        self._model.set_note(note)

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

    def _on_id_in_schedule_clicked(self, id_: int, type_: str, field: str):
        """Обрабатывает нажатие на id объекта в ScheduleWidget. Выводит информацию об объекте."""
        logging.debug(f'Field: {field} of object (ID: {id_}, type: {type_}) clicked.')

    def _on_id_clicked(self, type_: str, field: str):
        """Обрабатывает нажатие на ID объекта."""
        logging.debug(f'Field: {field} of object (type: {type_}) clicked in EventsTodayWidget.')

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
        logging.debug(f'User info received: {user_info}')
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
        self._window.delete_events_today_widget()

        for widget_type in self._data_const.names_widgets:
            result = self._model.get_widget_settings(widget_type)
            if not result:
                continue

            if widget_type == self._data_const.tasks_widget:
                self._task_widget = self._window.place_task_widget()
                self._task_widget.task_completed.connect(self._on_task_completed)
                self._get_task_handler_data()
                logging.debug('Tasks widget placed.')
            if widget_type == self._data_const.notes_widget:
                widget_view = self._window.place_notes_widget()
                self._notes_widget = widget_view
                note = self._model.get_note()
                self._notes_widget.set_notes(note)
                self._notes_widget.text_changed.connect(self._on_note_changed)
                logging.debug('Notes widget placed')
            if widget_type == self._data_const.schedule_widget:
                current_style = self._model.get_current_style()
                style = self._model.get_style(current_style)
                if current_style == DataStructConst.dark_style:
                    marking_color = DataStructConst.light_marking_color
                else:
                    marking_color = DataStructConst.dark_marking_color

                schedule_widget = self._window.place_schedule_widget(marking_color, style)
                events_today_widget = self._window.place_events_today_widget()
                self._schedule_view_handler = schedule_widget
                self._events_today_widget = events_today_widget
                self._get_schedule_widget_data()
                logging.debug('Schedule widget placed')
            if widget_type == self._data_const.reminder_widget:
                reminders = self._model.get_reminders()
                widget_view = self._window.place_reminder_widget()
                handler = ReminderViewHandler(widget_view)
                handler.set_max_reminder_length(DataStructConst.max_reminder_length)
                handler.set_reminders(reminders)
                handler.reminder_completed.connect(self._on_reminder_completed)
                handler.reminder_added.connect(self._on_reminder_added)
                handler.reminder_edited.connect(self._on_reminder_edited)
                logging.debug('Reminder widget placed')

    def _get_user_info(self) -> Request:
        request = self._requester.get_user_info(self._model.get_access_token())
        request.finished.connect(lambda response: self._prepare_request(response, self._set_user))
        self._requests.user_request = request
        return request

    def update_state(self):
        logging.debug('UserFlowWInHandler state updated')
        self._get_user_info()
        self._place_settable_widgets()

    def update_data(self):
        self._place_settable_widgets()

    def _set_personal_daily_events(self, events: tuple[dict, ...]):
        logging.debug(f'Personal daily events received: {events}.')
        if events:
            self._data_model.personal_daily_events = [cm.PersonalDailyEvent(**event) for event in events]

    def _set_personal_many_days_events(self, events: tuple[dict, ...]):
        logging.debug(f'Personal many days events received.')
        if events:
            self._data_model.personal_many_days_events = [cm.PersonalManyDaysEvent(**event) for event in events]

    def _set_wf_many_days_events(self, events: tuple[dict, ...]):
        logging.debug(f'WF many days events received.')
        if events:
            self._data_model.wf_many_days_events = [cm.WFManyDaysEvent(**event) for event in events]

    def _set_wf_daily_events(self, events: tuple[dict, ...]):
        logging.debug(f'WF daily events received')
        if events:
            self._data_model.wf_daily_events = [cm.WFDailyEvent(**event) for event in events]

    def _set_schedule_widget(self):
        logging.debug(f'Setting schedule widget. Events data received: '
                      f'WFDaily: {self._data_model.wf_daily_events and True}. '
                      f'WFManyDays: {self._data_model.wf_many_days_events and True}. '
                      f'PersonalDaily: {self._data_model.personal_daily_events and True}. '
                      f'PersonalManyDays: {self._data_model.personal_many_days_events and True}')
        daily_events = []
        for events in [self._data_model.wf_daily_events, self._data_model.personal_daily_events]:
            if events:
                daily_events.extend(events)

        many_days_events = []
        for events in [self._data_model.wf_many_days_events, self._data_model.personal_many_days_events]:
            if events:
                many_days_events.extend(events)

        for event in daily_events:
            time_start = event.time_start.strftime('%H:%M')
            time_end = event.time_end.strftime('%H:%M')
            description = {
                f'{GuiLabels.title}:': f'{time_start}-{time_end}.',
                f'{GuiLabels.description}': event.description,
                f'{GuiLabels.lasting}:': get_lasting(event.time_start, event.time_end)
            }

            if event.__tablename__ == ObjectTypes.wf_daily_event:
                event: cm.WFDailyEvent
                description.update({
                    f'{GuiLabels.title}:': f'{time_start}-{time_end}.',
                    f'{GuiLabels.workflow}': f'#{event.workflow_id}',
                    f'{GuiLabels.creator}': f'#{event.creator_id}',
                    f'{GuiLabels.description}': event.description,
                    f'{GuiLabels.notifieds}': iterable_to_str(event.notified, ',', '#')
                })
            self._schedule_view_handler.add_event(event.id, event.__tablename__, event.name, time_start, time_end, description)
        self._schedule_view_handler.event_tooltip_content_clicked.connect(self._on_id_clicked)

        for event in many_days_events:
            event: cm.WFManyDaysEvent
            date_start = event.datetime_start.date().strftime(DataStructConst.gui_month_date_format)
            date_end = event.datetime_end.date().strftime(DataStructConst.gui_month_date_format)
            lasting = event.datetime_end.date() - event.datetime_start.date()

            description = {
                f'{GuiLabels.title}:': event.name,
                f'{GuiLabels.lasting}:': f'{lasting.days} {GuiLabels.days}'
                           }

            if event.__tablename__ == ObjectTypes.wf_many_days_event:
                description.update({
                    f'{GuiLabels.workflow}': f'#{event.workflow_id}',
                    f'{GuiLabels.creator}:': f'#{event.creator_id}',
                    f'{GuiLabels.notifieds}:': f'{iterable_to_str(event.notified, ',', '#')}'
                })

            wdg_event = self._events_today_widget.add_event(event.name, date_start, date_end, description)

            if event.__tablename__ == ObjectTypes.wf_many_days_event:
                wdg_event.tooltip_content_clicked.connect(lambda field: self._on_id_clicked(ObjectTypes.wf_many_days_event, field))

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
            self._requests.personal_daily_events_request = personal_daily_events

            personal_many_days_events = self._requester.get_personal_many_days_events(self._data_model.user.id, access_token,
                                                                                      datetime.date.today())
            personal_many_days_events.finished.connect(lambda request: self._prepare_request(request, self._set_personal_many_days_events))
            self._requests.personal_many_days_events_request = personal_many_days_events

            wf_daily_events = self._requester.get_wf_daily_events_by_user(self._data_model.user.id,
                                                                          self._data_model.user.notified_daily_events,
                                                                          access_token,
                                                                          datetime.date.today(),
                                                                          )
            wf_daily_events.finished.connect(lambda request: self._prepare_request(request, self._set_wf_daily_events))
            self._requests.wf_daily_events = wf_daily_events

            wf_many_days_events = self._requester.get_wf_many_days_events_by_user(
                self._data_model.user.id,
                self._data_model.user.notified_many_days_events,
                access_token,
                datetime.date.today(),
                    )
            wf_many_days_events.finished.connect(lambda request: self._prepare_request(request, self._set_wf_many_days_events))
            self._requests.wf_many_days_event = wf_many_days_events

            group = self._requester.create_group(personal_daily_events, personal_many_days_events, wf_daily_events,
                                                 wf_many_days_events)
            group.finished.connect(lambda request: self._set_schedule_widget())

        else:
            self._prepare_no_data(self._get_user_info, self._requests.user_request, self._get_schedule_widget_data)

    def _get_task_handler_data(self):
        """Получает данные для обработчика задач и вызывает методы для его настройки."""
        access_token = self._model.get_access_token()

        if self._data_model.user:
            personal_tasks = self._requester.get_personal_tasks(self._data_model.user.id, access_token, datetime.date.today())
            personal_tasks.finished.connect(lambda request_: self._prepare_request(request_, self._set_personal_tasks))
            wf_tasks = self._requester.get_wf_tasks_by_user(self._data_model.user.id, access_token, datetime.date.today())
            wf_tasks.finished.connect(lambda request_: self._prepare_request(request_, self._set_wf_tasks))
            self._requests.wf_tasks_request = wf_tasks
            self._requests.personal_tasks_request = personal_tasks

            group = self._requester.create_group(personal_tasks, wf_tasks)
            group.finished.connect(lambda _: self._set_tasks_widget())
        else:  # Если данных не получено
            self._prepare_no_data(self._get_user_info, self._requests.user_request, self._get_task_handler_data)


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


@dataclasses.dataclass
class UserFlowRequests:
    """Датакласс, содержащий запросы UserFlow."""

    user_request: Request | None = None
    personal_tasks_request: Request | None = None
    wf_tasks_request: Request | None = None
    personal_daily_events_request: Request | None = None
    personal_many_days_events_request: Request | None = None
    wf_daily_events: Request | None = None
    wf_many_days_event: Request | None = None
