"""Класс для работы с кэшем."""

import datetime

from client.src.requester.requester import Requester, Request
from client.src.requester.requester_interface import IRequests
from client.src.client_model.model import Model


class CashManager(IRequests):

    def __init__(self, requester: Requester, model: Model):
        self._requester = requester
        self._model = model

    def get_user_info(self, access_token: str):
        return self._requester.get_user_info()

    def get_personal_tasks(self, user_id: int, access_token: str, on_date: datetime.date, tasks_ids: list[int] = None,
                           limit: int = None, offset: int = None) -> Request:
        """
        Получает личные задачи (конкретную или по user_id).
        :param user_id: ID владельца задачи.
        :param access_token: access-токен.
        :param on_date: Дата, на которую запланирована работа над задачей.
        :param tasks_ids: ID задач.
        """
        return self._requester.get_personal_tasks(user_id, access_token, on_date, tasks_ids, limit, offset)

    def get_wf_daily_events_by_user(self, user_id: int, wf_daily_events_ids: list[int], access_token: str,
                                          date: datetime.date = None, limit: int = None, offset: int = 0):
        return self._requester.get_wf_daily_events_by_user(user_id, wf_daily_events_ids, access_token, date, limit, offset)

    def get_wf_many_days_events_by_user(self, user_id: int, wf_many_days_events_ids: list[int], access_token: str,
                                              date: datetime.date = None, limit: int = None, offset: int = None):
        return self._requester.get_wf_many_days_events_by_user(user_id, wf_many_days_events_ids, access_token,
                                                               date, offset)

    def get_personal_many_days_events(self, user_id: int, access_token: str, date: datetime.date = None,
                                            limit: int = None, offset: int = None):
        return self._requester.get_personal_many_days_events(user_id, access_token, date, limit, offset)

    def get_personal_daily_events(self, user_id: int, access_token: str, date: datetime.date = None, limit: int = None,
                                  offset: int = None):
        return self._requester.get_personal_daily_events(user_id, access_token, date, limit, offset)

    def get_wf_tasks_by_user(self, user_id: int, access_token: str, date: datetime.date = None, limit: int = None,
                             offset: int = None):
        return self._requester.get_wf_tasks_by_user(user_id, access_token, date, limit, offset)

    def get_wf_tasks(self, tasks_ids: list[int], access_token: str, limit: int = None, offset: int = 0) -> Request:
        return self._requester.get_wf_tasks(tasks_ids, access_token, limit, offset)

    def get_users(self, ids: tuple[int, ...]) -> Request:
        access_token = self._model.get_access_token()
        return self._requester.get_users(ids, access_token)

    def get_workspaces(self, ids: tuple[int, ...]) -> Request:
        access_token = self._model.get_access_token()
        return self._requester.get_workspaces(ids, access_token)
