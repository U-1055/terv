from client.src.client_model.model import Model


class TestModel:
    """Класс для работы с файлами клиента."""

    def __init__(self, storage: str, data_root: str):
        pass

    def set_note(self, text: str):
        pass

    def get_note(self) -> str:
        pass

    def set_access_token(self, token_: str):
        pass

    def set_refresh_token(self, token_: str):
        pass

    def get_access_token(self) -> str:
        pass

    def get_refresh_token(self) -> str:
        pass

    def get_current_style(self) -> str:
        pass

    def set_current_style(self, style_name: str):
        pass

    def get_style(self, style_path: str) -> str:
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

    def add_reminder(self, reminder: str):
        """Добавляет напоминание."""
        pass

    def get_reminders(self) -> tuple[str, ...]:
        pass

    def delete_reminder(self, reminder: str):
        pass

    def set_reminders(self, reminders: tuple[str, ...] | list[str]):
        pass

    def clear_reminders(self):
        pass

    def set_style(self, style_name: str, style_color: str):
        pass

    def get_style_color(self, style_name: str) -> str:
        pass


