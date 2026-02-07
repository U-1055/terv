"""
Модуль для работы с файлами клиента.

Структура хранилища:
{
    settings: {
        style: <style>
    }

    userflow_widgets: {
        <widget_name>: {'x': int, 'y': int, 'x_size': int, 'y_size': int}
    }
    note: <Текст локальной заметки>
    reminders: [] <Список напоминаний пользователя>

    access_token: <access_token>

    refresh_token: <refresh_token>

}

"""
import logging
import shelve
from pathlib import Path

from client.src.base import DataStructConst

userflow_widget = {'x': 0, 'y': 0, 'x_size': 0, 'y_size': 0}


class Model:
    """Класс для работы с файлами клиента."""

    default_struct = {
        DataStructConst.access_token: '',
        DataStructConst.refresh_token: '',
        DataStructConst.note: '',
        DataStructConst.settings: {DataStructConst.style: ''},
        DataStructConst.reminders: [],
        DataStructConst.userflow_widgets: dict()
                      }

    def __init__(self, storage: Path, data_root: Path, data_struct_const: DataStructConst = DataStructConst()):
        self._storage = storage
        self._data_root = data_root
        self._ds_const = data_struct_const

        self._check_storage_struct()

    def _check_storage_struct(self):
        with shelve.open(self._storage) as storage:
            for key in self.default_struct:
                if key not in storage:
                    storage[key] = self.default_struct[key]
                    logging.warning(f'There is no field {key} in {self._storage} file. Field has been set to default '
                                    f'value: {self.default_struct[key]}')

                field_type = type(storage[key])
                expected_field_type = type(self.default_struct[key])
                if field_type is not expected_field_type:
                    storage[key] = self.default_struct[key]
                    logging.warning(f'Incorrect type of field {key} of file {self._storage} - '
                                    f'type "{field_type}" must be "{expected_field_type}". Field {key} has been set'
                                    f'to default value: {self.default_struct[key]}.')

            if not storage[self._ds_const.settings].get(self._ds_const.style):
                storage[self._ds_const.settings] = self.default_struct[self._ds_const.settings]
                logging.warning(f'There is no field "style" in field "settings" in file. Field '
                                f'"{self._ds_const.settings}" has been set to default value: '
                                f'{self.default_struct[self._ds_const.settings]}.')

    def set_note(self, text: str):
        with shelve.open(self._storage, 'w') as storage:
            storage[self._ds_const.note] = text

    def get_note(self) -> str:
        with shelve.open(self._storage) as storage:
            return storage.get(self._ds_const.note)

    def set_access_token(self, token_: str):
        logging.info(f'Set new access token: {token_}.')
        with shelve.open(self._storage, 'w') as storage:
            storage[self._ds_const.access_token] = token_

    def set_refresh_token(self, token_: str):
        logging.info(f'Set new refresh token: {token_}.')
        with shelve.open(self._storage, 'w') as storage:
            storage[self._ds_const.refresh_token] = token_

    def get_access_token(self) -> str:
        with shelve.open(self._storage) as storage:
            token_ = storage[self._ds_const.access_token]
            return token_

    def get_refresh_token(self) -> str:
        with shelve.open(self._storage) as storage:
            token_ = storage[self._ds_const.refresh_token]
            return token_

    def get_style(self) -> str:
        with shelve.open(self._storage) as storage:
            token_ = storage[self._ds_const.settings][self._ds_const.style]
            return token_

    def put_widget_settings(self, wdg_type: str, x: int, y: int, x_size: int, y_size: int):
        """Добавляет настройки виджета. Если виджет уже настроен - обновляет настройки на введённые."""

        with shelve.open(self._storage, 'w') as storage:
            struct_ = {wdg_type:
                {
                    self._ds_const.x: x,
                    self._ds_const.y: y,
                    self._ds_const.x_size: x_size,
                    self._ds_const.y_size: y_size
                }
            }
            dict_ = storage[self._ds_const.userflow_widgets]
            dict_.update(struct_)
            storage[self._ds_const.userflow_widgets] = dict_

    def get_widget_settings(self, wdg_type: str) -> dict | None:
        """
        Возвращает настройки виджета. Если виджета нет в настройках (не настроен или неверный тип) - возвращает None.
        """
        with shelve.open(self._storage) as storage:
            settings = storage[self._ds_const.userflow_widgets].get(wdg_type)
            return settings

    def delete_widget_settings(self, wdg_type: str):
        """Удаляет настройки виджета."""
        with shelve.open(self._storage, 'w') as storage:
            dict_ = storage[self._ds_const.userflow_widgets]
            if wdg_type in dict_:
                dict_.pop(wdg_type)
            storage[self._ds_const.userflow_widgets] = dict_

    def add_reminder(self, reminder: str):
        """Добавляет напоминание."""
        with shelve.open(self._storage, 'w') as storage:
            reminders = storage[self._ds_const.reminders]
            reminders.append(reminder)
            storage[self._ds_const.reminders] = reminders

    def get_reminders(self) -> tuple[str, ...]:
        with shelve.open(self._storage) as storage:
            reminders = storage[self._ds_const.reminders]
            return reminders

    def delete_reminder(self, reminder: str):
        with shelve.open(self._storage, 'w') as storage:
            reminders = storage[self._ds_const.reminders]
            reminders.remove(reminder)
            storage[self._ds_const.reminders] = reminders

    def set_reminders(self, reminders: tuple[str, ...] | list[str]):
        with shelve.open(self._storage, 'w') as storage:
            storage[self._ds_const.reminders] = reminders

    def clear_reminders(self):
        with shelve.open(self._storage, 'w') as storage:
            storage[self._ds_const.reminders] = []


if __name__ == '__main__':
    model = Model(Path('..\\..\\data\\config_data\\storage'), Path('..\\..\\data'), DataStructConst())
    model.put_widget_settings(DataStructConst.tasks_widget, 0, 0, 0, 0)

    reminders = [f'reminder_{i}' for i in range(100)]
    model.set_reminders(reminders)

