"""Обработчик окна списка рабочих пространств."""
from PySide6.QtCore import Signal

from client.src.src.handlers.window_handlers.base import BaseWindowHandler
from client.src.gui.windows.workspaces_window import WorkspacesListWindow
from client.src.requester.requester import Requester
from client.src.gui.main_view import MainWindow
from client.src.client_model.model import Model
import client.models.common_models as cm
from common.logger import config_logger, CLIENT
from client.src.base import LOG_DIR, MAX_FILE_SIZE, MAX_BACKUP_FILES, LOGGING_LEVEL

logger = config_logger(__name__, CLIENT, LOG_DIR, MAX_FILE_SIZE, MAX_BACKUP_FILES, LOGGING_LEVEL)


class WorkspacesListWindowHandler(BaseWindowHandler):
    """
    Обработчик окна списка рабочих пространств.
    
    Управляет отображением рабочих пространств пользователя, поиском и фильтрацией.
    
    :var workspace_data_received: Сигнал, испускаемый при получении данных о рабочих пространствах.
    :var tried_to_open_workspace: Сигнал, испускаемый при попытке открыть рабочее пространство.
    """
    
    workspace_data_received = Signal(list)  # Передаёт список рабочих пространств
    tried_to_open_workspace = Signal(int, str)  # Передаёт ID и название рабочего пространства
    tried_to_open_workspace = Signal(int, str)  # Передаёт ID и название рабочего пространства

    def __init__(self, window: WorkspacesListWindow, main_view: MainWindow, requester: Requester, model: Model):
        super().__init__(window, main_view, requester, model)
        
        self._window: WorkspacesListWindow = window
        self._requester = requester
        self._model = model
        self._user_id: int | None = None

        # Подключение сигналов окна
        self._window.search_pressed.connect(self._on_search_pressed)
        self._window.reset_pressed.connect(self._on_reset_pressed)
        self._window.workspace_clicked.connect(self._on_workspace_clicked)
        
        # Хранение данных о рабочих пространствах
        self._workspaces: list[cm.Workspace] = []
    
    def _on_workspace_data_received(self, data: dict):
        """
        Обрабатывает полученные данные о рабочих пространствах.
        
        :param data: преобразованный в JSON ответ.
        """
        if not data or not data.get('content'):
            return

        self._workspaces.clear()
        self._window.clear_widgets()

        for ws_data in data.get('content'):
            workspace = cm.Workspace(**ws_data)
            self._workspaces.append(workspace)
            print(workspace)
            # Добавление виджета рабочего пространства
            widget = self._window.add_workspace_widget(
                name=workspace.name,
                description=workspace.description if hasattr(workspace, 'description') else '',
                workspace_id=workspace.id
            )
            widget.open_pressed.connect(lambda: self.try_to_open_workspace(workspace.id, workspace.name))

        self.workspace_data_received.emit(self._workspaces)
        logger.info(f'Workspaces loaded: {len(self._workspaces)} workspaces')
    
    def _on_search_pressed(self, search_text: str):
        """
        Обрабатывает запрос на поиск рабочих пространств.
        
        :param search_text: Поисковая строка.
        """
        self._window.filter_widgets(search_text)
    
    def _on_reset_pressed(self):
        """Обрабатывает сброс поиска."""
        self._window.clear_search()
        self._window.filter_widgets('')
        self._window.set_reset_button_enabled(False)
    
    def _on_workspace_clicked(self, workspace_id: int):
        """
        Обрабатывает клик по рабочему пространству.
        
        :param workspace_id: ID выбранного рабочего пространства.
        """
        logger.info(f'Workspace clicked: {workspace_id}')

        # Получаем название рабочего пространства
        workspace = self.get_workspace_by_id(workspace_id)
        workspace_name = workspace.name if workspace else f'Workspace {workspace_id}'

        # Испускаем сигнал открытия рабочего пространства
        self.try_to_open_workspace(workspace_id, workspace_name)

    def try_to_open_workspace(self, id_: int, name: str):
        self.tried_to_open_workspace.emit(id_, name)

    def set_user_id(self, id_: int):
        self._user_id = id_

    def update_state(self):
        """
        Обновляет состояние обработчика.
        
        Загружает данные о рабочих пространствах пользователя с сервера.
        """
        logger.info('Updating workspaces list')
        
        access_token = self._model.get_access_token()
        
        # Запрос на получение рабочих пространств пользователя
        request = self._requester.get_workspaces_by_user(
            user_id=self._user_id,
            access_token=access_token,
            limit=100,
            offset=0
        )
        
        request.finished.connect(lambda req: self._prepare_request(req, self._on_workspace_data_received))
    
    def update_data(self):
        """Обновляет данные в обработчике."""
        self.update_state()
    
    def workspaces(self) -> list[cm.Workspace]:
        """Возвращает список рабочих пространств."""
        return self._workspaces
    
    def get_workspace_by_id(self, workspace_id: int) -> cm.Workspace | None:
        """
        Возвращает рабочее пространство по его ID.
        
        :param workspace_id: ID рабочего пространства.
        """
        for workspace in self._workspaces:
            if workspace.id == workspace_id:
                return workspace
        return None
