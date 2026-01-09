import datetime
import logging
import time

logging.basicConfig(level=logging.DEBUG)
logging.debug('Module timeout_dict.py is running')


class TimeoutDict(dict):
    """
    Словарь c тайм-аутом, по прошествии которого с момента добавления элемента тот будет удалён.
    Хранит элементы как: {key: (value, <время удаления>)}

    :param timeout: время (в секундах) по прошествии которого с момента добавления элемента в словарь он будет удалён.
    Если None - элементы удаляться не будут.
    """

    def __init__(self, timeout: int = None):
        super().__init__()
        self._timeout = timeout

    def set_timeout(self, timeout: int):
        self._timeout = timeout

    def timeout(self) -> int:
        return self._timeout

    def update_elements(self):
        """Удаляет значения с истёкшим временем."""
        for key in list(self.keys()):
            if super().get(key)[1] < datetime.datetime.now():
                self.pop(key)
        logging.debug(f'TimeoutDict.update_elements has been called. Dict now: {self}')

    def __setitem__(self, key, value):
        super().update({key:  (value, datetime.datetime.now() + datetime.timedelta(seconds=self._timeout))})  # Элемент + время удаления

    def __getitem__(self, item):
        return super().get(item)[0]

    def __str__(self):
        return ''.join(['{', *[f'{str(key)}: {str(self[key])}, ' for key in self], '}'])

    def values(self):
        return [el[0] for el in super().values()]


if __name__ == '__main__':
    dict_ = TimeoutDict(5)
    for i in range(10):
        dict_[i] = 5

    time.sleep(6)
    dict_.update_elements()
