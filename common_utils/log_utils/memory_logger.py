import matplotlib.pyplot as pyplot
import psutil

import time
import datetime
import os

from pathlib import Path


def plot(path: str | Path):
    """
    Строит график потребления памяти по данным из файла root/log/memory.txt
    Формат файла с данными о памяти:
    datetime.datetime (в стандартном формате) | MEMORY: <float, округлённый до 2-х знаков после точки> MB
    """

    with open(path) as file:
        lines = file.readlines()
        data = []
        for line in lines:
            if 'START CHECKING' in line:
                continue
            spl_line = line.split('MEMORY: ')[1]
            spl_line = spl_line.split()[0]
            data.append(float(spl_line))

        pyplot.figure()
        pyplot.plot(range(0, len(data) * 2, 2), data)
        pyplot.show()


def get_memory_data(path: str | Path) -> tuple[float, float, float]:
    """
    Возвращает данные о потребляемой памяти: (<среднее значение памяти>, <минимальное>, <максимальное>).

    :param path: Путь к файлу с данными о памяти

    """
    with open(path) as file:
        lines = file.readlines(10000)
        memory_values = []

        while lines:
            for line in lines:
                if ':' not in line or 'START CHECKING' in line:
                    continue

                memory = line.split(':')[-1].split()[0].strip()
                memory_values.append(float(memory))

            lines = file.readlines(10000)

    middle = round(sum(memory_values) / len(memory_values), 2)
    max_ = max(memory_values)
    min_ = min(memory_values)

    return middle, min_, max_


def check_memory(file_path: Path, late: int = 2):
    """
    :param file_path: Путь к файлу.
    :param late: Задержка между записями (в сек.). По умолчанию: 2.
    """
    process = psutil.Process(os.getpid())

    with open(file_path, 'a') as file:
        file.write(f'START CHECKING: [{datetime.datetime.now()}]\n')

    while True:
        time.sleep(late)
        with open(file_path, 'a') as file:
            file.write(f'{datetime.datetime.now()}| MEMORY: {round(process.memory_info().rss / 1024 / 1024, 2)} MB\n')


if __name__ == '__main__':
    data = get_memory_data('../../log/memory_server.txt')
    print(
        f'MIDDLE: {data[0]} MB | MIN: {data[1]} MB | MAX: {data[2]} MB'
    )
    plot('../../log/memory_server.txt')


