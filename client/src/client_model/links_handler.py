"""Класс для работы со ссылками на ID объектов."""
from PySide6.QtCore import QTimer

from pathlib import Path
import shelve

from client.src.requester.cash_manager import CashManager, Request
from client.models.common_models import User, Workspace, WFTask, PersonalTask


class LinksHandler:

    def __init__(self, links_storage_path: Path, cash_manager: CashManager | None = None):
        self._links_models = LinksModel(links_storage_path)
        self._cash = cash_manager

    def get_user(self, user_id: int) -> Request | User:
        user = self._links_models.get_user(user_id)
        if user:
            return user

        return self._cash.get_users((user_id,))

    def get_workspace(self, workspace_id: int) -> Request | Workspace:
        workspace = self._links_models.get_workspace(workspace_id)
        if workspace:
            return workspace
        return self._cash.get_workspaces((workspace_id,))

    def add_workspace(self, workspace: Workspace):
        self._links_models.add_workspace(workspace)

    def add_user(self, user: User):
        self._links_models.add_user(user)

    def add_wf_task(self):
        pass

    def add_personal_task(self):
        pass

    def set_cash_manager(self, cash_manager: CashManager):
        self._cash = cash_manager


class LinksModel:

    users = 'users'
    workspaces = 'workspaces'
    wf_tasks = 'wf_tasks'
    personal_tasks = 'personal_tasks'

    def __init__(self, storage_path: Path, timeout: int = 60000):
        self._storage_path = storage_path
        self._timeout = timeout
        self._update()

    def _update(self):
        with shelve.open(self._storage_path) as storage:
            storage[self.users] = dict()
            storage[self.workspaces] = dict()
            storage[self.wf_tasks] = dict()
            storage[self.personal_tasks] = dict()
        QTimer.singleShot(self._timeout, self._update)

    def get_user(self, user_id: int) -> User | None:
        with shelve.open(self._storage_path) as storage:
            users = storage.get(self.users)
            if users:
                user = users.get(user_id)
                return User(**user)

    def get_wf_task(self, task_id: int) -> WFTask | None:
        with shelve.open(self._storage_path) as storage:
            tasks = storage.get(self.wf_tasks)
            if tasks:
                task = tasks.get(task_id)
                return WFTask(**task)

    def get_personal_task(self, task_id: int) -> PersonalTask | None:
        with shelve.open(self._storage_path) as storage:
            tasks = storage.get(self.personal_tasks)
            if tasks:
                task = tasks.get(task_id)
                return PersonalTask(**task)

    def get_workspace(self, workspace_id: int) -> Workspace | None:
        with shelve.open(self._storage_path) as storage:
            workspaces = storage.get(self.workspaces)
            if workspaces:
                workspace = workspaces.get(workspace_id)
                return Workspace(**workspace)

    def add_workspace(self, workspace: Workspace):
        with shelve.open(self._storage_path, 'w') as storage:
            workspaces = storage[self.workspaces]
            workspaces[workspace.id] = workspace.serialize()
            storage[self.workspaces] = workspaces

    def add_user(self, user: User):
        with shelve.open(self._storage_path, 'w') as storage:
            users = storage.get(self.users)
            users[user.id] = user.serialize()
            storage[self.users] = users

