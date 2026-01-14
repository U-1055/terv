from client.src.client_model.model import Model


class TestModel(Model):
    """Класс для работы с файлами клиента."""

    def __init__(self, storage: str, data_root: str):
        super().__init__(storage, data_root)
        self._access_token = None
        self._refresh_token = None

    def set_access_token(self, token_: str):
        self._access_token = token_

    def set_refresh_token(self, token_: str):
        self._refresh_token = token_

    def get_access_token(self) -> str:
        return self._access_token

    def get_refresh_token(self) -> str:
        return self._refresh_token

    def get_style(self) -> str:
        pass

    def put_widget_settings(self, wdg_type: str, x: int, y: int, x_size: int, y_size: int):
        """Добавляет настройки виджета. Если виджет уже настроен - обновляет настройки на введённые."""
        pass

    def get_widget_settings(self, wdg_type: str) -> dict | None:
        """
        Возвращает настройки виджета. Если виджета нет в настройках (не настроен или неверный тип) - возвращает None.
        """
        pass

    def delete_widget_settings(self, wdg_type: str):
        """Удаляет настройки виджета."""
        pass


