import asyncio
import logging
import time

from PySide6.QtCore import QTimer

import typing as tp

from client.src.src.handlers.window_handlers.base import BaseWindowHandler, MainWindow, Requester, Model, BaseWindow
from client.src.base import DataStructConst, widgets_labels, labels_widgets
from client.src.gui.widgets_view.base_view import BaseView
from client.src.src.handlers.widgets_view_handlers.userflow_handlers import TaskViewHandler
from client.src.gui.windows.userflow_window import UserFlowWindow
from client.src.gui.widgets_view.userflow_view import (TaskWidgetView, ScheduleWidgetView, NotesWidgetView,
                                                       WidgetSettingsMenu, ReminderWidgetView)
from client.src.src.handlers.widgets_view_handlers.userflow_handlers import (NotesViewHandler, ScheduleViewHandler,
                                                                             ReminderViewHandler)
from client.models.common_models import User, PersonalTask

from client.utils.data_tools import make_unique_dict_names


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
        self._notes_view_handler: NotesWidgetView = None
        self._schedule_view_handler: ScheduleWidgetView = None
        self._user: User = None

        self._window.btn_set_widgets_pressed.connect(self._on_btn_set_widgets_pressed)

        self._timer = QTimer()

    def _on_btn_set_widgets_pressed(self):
        selected_widgets = []
        for widget in DataStructConst.names_widgets:  # Выбираем виджеты, у которых есть настройки
            if self._model.get_widget_settings(widget):
                selected_widgets.append(widgets_labels.get(widget))

        widgets = [widgets_labels.get(widget) for widget in DataStructConst.names_widgets]

        settings_window = WidgetSettingsMenu(widgets, selected_widgets)
        settings_window.set.connect(self._set_widgets_settings)
        self._main_view.show_modal_window(settings_window)

    def _on_reminder_edited(self, last_name: str, current_name: str):
        self._model.delete_reminder(last_name)
        self._model.add_reminder(current_name)

    def _on_reminder_completed(self, reminder: str):
        self._model.delete_reminder(reminder)

    def _on_reminder_added(self, reminder: str):
        self._model.add_reminder(reminder)

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
        self._user = User(**user_info[0])

    def _set_tasks(self, tasks: tuple[dict, ...]):
        if not self._task_view_handler:
            return

        dicts = []
        for task in tasks:
            dicts.append({task[PersonalTask.name]: task[PersonalTask.id]})
        tasks_list = make_unique_dict_names(dicts)
        self._task_view_handler.tasks = tasks_list

    def _place_settable_widgets(self):
        self._window.delete_notes_widget()
        self._window.delete_tasks_widget()
        self._window.delete_reminder_widget()

        for widget_type in self._data_const.names_widgets:
            result = self._model.get_widget_settings(widget_type)
            if not result:
                continue

            x, y, x_size, y_size = (result.get(self._data_const.x), result.get(self._data_const.y),
                                    result.get(self._data_const.x_size), result.get(self._data_const.y_size))

            if widget_type == self._data_const.tasks_widget:
                widget_view = self._window.place_task_widget(x, y, x_size, y_size)
                self._set_task_handler(widget_view)
                logging.debug('Tasks widget placed.')
            if widget_type == self._data_const.notes_widget:
                widget_view = self._window.place_notes_widget(x, y, x_size, y_size)
                note = self._model.get_note()
                handler = NotesViewHandler(widget_view)
                handler.set_notes(note)
                logging.debug('Notes widget placed')
            if widget_type == self._data_const.schedule_widget:
                widget_view = self._window.place_schedule_widget()
                handler = ScheduleViewHandler(widget_view)
                logging.debug('Schedule widget placed')
            if widget_type == self._data_const.reminder_widget:
                reminders = self._model.get_reminders()
                widget_view = self._window.place_reminder_widget(x, y, x_size, y_size)
                handler = ReminderViewHandler(widget_view)
                handler.set_reminders(reminders)
                handler.reminder_completed.connect(self._on_reminder_completed)
                handler.reminder_added.connect(self._on_reminder_added)
                handler.reminder_edited.connect(self._on_reminder_edited)
                logging.debug('Reminder widget placed')

    def update_state(self):
        request: asyncio.Future = self._requester.get_user_info(self._model.get_access_token())
        request.add_done_callback(lambda future: self._prepare_request(future, self._set_user))

        self._place_settable_widgets()

    def _set_task_handler(self, view: TaskWidgetView):  # ToDo: логика запросов
        """Настраивает обработчик задач."""
        access_token = self._model.get_access_token()

        if self._user:
            tasks: asyncio.Future = self._requester.get_personal_tasks(self._user.id, access_token)
            tasks.add_done_callback(lambda future: self._prepare_request(future, self._set_tasks))
        else:
            request: asyncio.Future = self._requester.get_user_info(access_token)
            request.add_done_callback(lambda future: self._prepare_request(future, lambda: self._set_task_handler(view)))

