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

    access_token: <access_token>

    refresh_token: <refresh_token>

}

"""

import shelve
from pathlib import Path

from terv.src.base import DataStructConst

userflow_widget = {'x': 0, 'y': 0, 'x_size': 0, 'y_size': 0}


class Model:
    """Класс для работы с файлами клиента."""

    def __init__(self, storage: Path, data_root: Path, data_struct_const: DataStructConst = DataStructConst()):
        self._storage = storage
        self._data_root = data_root
        self._ds_const = data_struct_const

    def set_access_token(self, token_: str):
        with shelve.open(self._storage, 'w') as storage:
            storage[self._ds_const.access_token] = token_

    def set_refresh_token(self, token_: str):
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
            dict_.pop(wdg_type)
            storage[self._ds_const.userflow_widgets] = dict_


if __name__ == '__main__':
    model = Model(Path('..\\..\\data\\config_data\\storage'), Path('..\\..\\data'), DataStructConst())
    model.put_widget_settings(DataStructConst.tasks_widget, 1, 1, 2, 3)
    print(model.get_widget_settings(DataStructConst.tasks_widget))
