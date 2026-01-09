import datetime
import time
import typing as tp


class TimeoutList(list):
    """
    Список с тайм-аутом, по прошествии которого с момента добавления элемента вызывается переданная функция, в которую
    передаётся аргументом этот элемент.
    Если достигнута максимальная длина списка, при добавлении нового элемента будет удалён элемент, добавленный раньше всего.

    :param timeout:  тайм-аут.
    :param func: функция с сигнатурой вида func(value: tp.Any) -> None, в которую передаётся элемент списка с истёкшим тайм-аутом при обновлении списка
    :param max_length: максимальная длина списка.
    """

    def __init__(self, timeout: int = 0, func: tp.Callable[[tp.Any], None] = lambda a: None, max_length: int = -1):
        super().__init__()
        self._timeout = timeout
        self._func = func
        self._max_length = max_length
        self._timeouts = {}

    def _del_elements(self):
        """Удаляет элемент с наибольшим тайм-аутом. (Т.е. добавленный раньше всех)."""
        max_timeout_idx = 0
        for i in self._timeouts:
            if self._timeouts[i] < self._timeouts[max_timeout_idx]:
                max_timeout_idx = i

        self.pop(max_timeout_idx)

    def append(self, __object):
        if self._max_length > 0 and len(self) == self._max_length:
            self._del_elements()

        super().append(__object)
        self._timeouts[len(self) - 1] = datetime.datetime.now() + datetime.timedelta(seconds=self._timeout)  # Время удаления

    def pop(self, __index=-1):
        super().pop(__index)
        self._timeouts.pop(__index)
        for idx in self._timeouts:
            if idx > __index:
                value = self._timeouts.pop(idx)
                self._timeouts[idx - 1] = value

    def update(self):
        """Вызывает функцию, переданную при инициализации, передавая в неё аргументы с истёкшим тайм-аутом."""
        for idx in list(self._timeouts.keys()):
            if self._timeouts[idx] < datetime.datetime.now():
                self._func(self[idx])

    def remove(self, __value):
        for i, val in enumerate(self):
            if val == __value:
                self.pop(i)


if __name__ == '__main__':
    timeout_list = TimeoutList(2, print, 3)

    timeout_list.append('string1')
    timeout_list.append('string2')
    timeout_list.append('string3')
    time.sleep(5)
    timeout_list.update()
    timeout_list.append('string4')
    print(timeout_list)

