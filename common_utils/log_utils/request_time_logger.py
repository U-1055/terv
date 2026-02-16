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

    def _format_string(self, requester_func: tp.Callable, request: Request, time_status: str,
                       time_: datetime.datetime) -> str:
        converted_time = time_.minute * 60 * 1000 + time_.second * 1000  # Считаем с миллисекундах

        return f'Method: {requester_func}|Request-object: {request}|{time_status}: {converted_time}\n'

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
            less_count = 0  # Число значений, меньших чем указанное время
            val_count = 0  # Общее число значений

            while lines:
                requests = dict()
                times = []

                for line in lines:  # Составляем словарь
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

                times_ = sorted(times)
                for time_ in times_:  # Находим, сколько запросов попадают под перцентиль
                    if time_ > percentile_time:
                        break
                    less_count += 1
                val_count += len(times_)
                lines = file.readlines(10000)

            percentile = round(less_count / val_count, 4) * 100
            return percentile

    def clear(self):
        with open(self._path, 'w') as file:
            file.write('')


class LogLine:

    def __init__(self, line: str):
        spl_line = line.split('|')
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
    path = '../../log/requests_time.txt'
    util = RequestsTimeHandler(path)
    print(util.get_time_of_requests(1020))

