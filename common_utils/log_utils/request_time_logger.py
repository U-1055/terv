"""Утилита для записи времени выполнения запросов."""
import datetime
import logging
import pathlib
import random
import time
import typing as tp


if tp.TYPE_CHECKING:
    from client.src.requester.requester import Request
else:
    Request = ''


class RequestsTimeHandler:

    started = 'started'
    finished = 'finished'

    def __init__(self, requests_file_path: pathlib.Path):
        self._path = requests_file_path

    @staticmethod
    def _format_string(requester_func: tp.Callable, request: Request, time_status: str,
                       time_: datetime.datetime) -> str:
        converted_time = time_.minute * 60 * 1000 + time_.second * 1000  # Считаем с миллисекундах

        return f'Method: {requester_func}|Request-object: {request}|{time_status}: {converted_time}|[{datetime.datetime.now()}]\n'

    @staticmethod
    def _get_percentile(percentile_value: int, array: list) -> float:
        array = sorted(array)
        less_count = 0
        total = len(array)

        for val in array:
            if val > percentile_value:
                break
            less_count += 1
        return round(less_count / total, 4) * 100

    def start_request(self, requester_func: tp.Callable, request: Request):
        with open(self._path, 'a') as file:
            file.write(self._format_string(requester_func, request, self.started, datetime.datetime.now().time()))

    def finish_request(self, requester_func: tp.Callable, request: Request):
        with open(self._path, 'a') as file:
            file.write(self._format_string(requester_func, request, self.finished, datetime.datetime.now().time()))

    def get_time_of_requests(self, percentile_time: int) -> float:
        """
        Рассчитывает перцентиль по запросам, выполняющимся за указанное время. Возвращает перцентиль (процент запросов,
        которые выполняются не более чем за переданное время).

        :param percentile_time: Время выполнения запроса (в мс).

        """
        with open(self._path) as file:
            lines = file.readlines(10000)
            times = []

            while lines:
                requests = dict()

                for line in lines:  # Составляем словарь
                    if ':' not in line:
                        continue
                    line = LogLine(line)
                    if line.request not in requests and line.type_ == self.started:
                        requests[line.request] = [line.time]
                    if line.type_ == self.finished and line.request in requests:
                        requests[line.request].append(line.time)

                for request in requests.values():  # Находим время выполнения запросов
                    if len(request) != 2:
                        logging.warning(f'There is no finish time of request. {request}')
                        continue

                    time_ = request[1] - request[0]
                    times.append(time_)

                lines = file.readlines(10000)

            percentile = self._get_percentile(percentile_time, times)
            return percentile

    def clear(self):
        with open(self._path, 'w') as file:
            file.write('')


class LogLine:

    def __init__(self, line: str):
        spl_line = line.split('|')
        if len(spl_line[0].split(':')) != 2:
            print(line)

        self._requester_method = spl_line[0].split(':')[1].strip()
        self._request = spl_line[1].split(':')[1].strip()
        self._time = int(spl_line[2].split(':')[1])
        self._type = spl_line[2].split(':')[0].strip()

    @property
    def requester_method(self) -> str:
        return self._requester_method

    @property
    def request(self) -> str:
        return self._request

    @property
    def time(self) -> int:
        return self._time

    @property
    def type_(self) -> str:
        return self._type


if __name__ == '__main__':
    path = '../../log/requests_time_load.txt'
    util = RequestsTimeHandler(path)
    print(util.get_time_of_requests(1000))

