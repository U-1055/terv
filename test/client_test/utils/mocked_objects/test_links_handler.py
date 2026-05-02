"""Фальшивые LinksHandler и CashManager."""

class TestLinksHandler:
    def __init__(self, links_storage_path, cash_manager: 'TestCashManager' = None):
        pass

    def get_user(self, user_id: int):
        pass

    def get_workspace(self, workspace_id: int):
        pass

    def add_workspace(self, workspace):
        pass

    def add_user(self, user):
        pass

    def add_ws_task(self):
        pass

    def add_personal_task(self):
        pass

    def set_cash_manager(self, cash_manager):
        pass


class TestCashManager:
    def __init__(self, requester, model):
        self._requester = requester
        self._model = model

    def get_user_info(self, access_token: str):
        pass

    def get_personal_tasks(self, user_id: int, access_token: str, on_date, tasks_ids: list[int] = None,
                           limit: int = None, offset: int = None):
        pass

    def get_ws_daily_events_by_user(self, user_id: int, ws_daily_events_ids: list[int], access_token: str,
                                          date = None, limit: int = None, offset: int = 0):
        pass

    def get_ws_many_days_events_by_user(self, user_id: int, ws_many_days_events_ids: list[int], access_token: str,
                                        date = None, limit: int = None, offset: int = None):
        pass

    def get_personal_many_days_events(self, user_id: int, access_token: str, date = None,
                                      limit: int = None, offset: int = None):
        pass

    def get_personal_daily_events(self, user_id: int, access_token: str, date = None, limit: int = None,
                                  offset: int = None):
        pass

    def get_ws_tasks_by_user(self, user_id: int, access_token: str, date = None, limit: int = None,
                             offset: int = None):
        pass

    def get_ws_tasks(self, tasks_ids: list[int], access_token: str, limit: int = None, offset: int = 0):
        pass

    def get_users(self, ids: tuple[int, ...]):
        pass

    def get_workspaces(self, ids: tuple[int, ...]):
        pass
