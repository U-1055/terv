"""Интерфейс запросов."""
from abc import abstractclassmethod, ABC
import datetime

import typing as tp

if tp.TYPE_CHECKING:
    from client.src.requester.requester import Response, InternalRequest
else:
    Response = ''
    InternalRequest = ''


class IRequests(ABC):
    """Интерфейс запросов."""

    def register(self, login: str, password: str, email: str) -> Response:
        pass

    def update_tokens(self, refresh_token: str) -> Response:
        pass

    def recall_tokens(self, *tokens: str) -> Response:
        pass

    def authorize(self, login: str, password: str) -> Response:
        pass

    def get_user_info(self, access_token: str) -> Response:
        pass

    def get_personal_tasks(self, user_id: int, access_token: str, on_date: datetime.date, tasks_ids: list[int] = None,
                                 limit: int = None, offset: int = None) -> Response:
        """
        Получает личные задачи (конкретную или по user_id).
        :param user_id: ID владельца задачи.
        :param access_token: access-токен.
        :param on_date: Дата, на которую запланирована работа над задачей.
        :param tasks_ids: ID задач.
        """

    def get_wf_daily_events_by_user(self, user_id: int, wf_daily_events_ids: list[int], access_token: str,
                                          date: datetime.date = None, limit: int = None, offset: int = 0):
        pass

    def get_wf_many_days_events_by_user(self, user_id: int, wf_many_days_events_ids: list[int], access_token: str,
                                              date: datetime.date = None, limit: int = None, offset: int = None):
        pass

    def get_personal_many_days_events(self, user_id: int, access_token: str, date: datetime.date = None,
                                            limit: int = None, offset: int = None):
        pass

    def get_personal_daily_events(self, user_id: int, access_token: str, date: datetime.date = None, limit: int = None,
                                  offset: int = None):
        pass

    def get_wf_tasks_by_user(self, user_id: int, access_token: str, date: datetime.date = None, limit: int = None,
                             offset: int = None):
        pass

    def get_wf_tasks(self, tasks_ids: list[int], access_token: str, limit: int = None, offset: int = 0) -> Response:
        pass

    def set_wf_task_status(self, wf_task_id: int, status: str, access_token: str):
        """Изменяет статус задачи РП."""
        pass

    def set_personal_task_status(self, personal_task_id: int, status: str, access_token: str):
        """Изменяет статус личной задачи."""
        pass

    def retry(self, access_token: str, request: InternalRequest) -> Response:
        """
        Повторяет один из предыдущих запросов, предварительно меняя его access_token на переданный.
        :param access_token: access токен.
        :param request: запрос.
        """
        pass
