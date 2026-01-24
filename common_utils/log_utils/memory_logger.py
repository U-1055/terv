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
            spl_line = line.split('MEMORY: ')[1]
            spl_line = spl_line.split()[0]
            data.append(float(spl_line))

        pyplot.figure()
        pyplot.plot(range(0, len(data) * 2, 2), data)
        pyplot.show()


def check_memory(file_path: Path):
    process = psutil.Process(os.getpid())
    while True:
        time.sleep(2)
        with open(file_path, 'a') as file:
            file.write(f'{datetime.datetime.now()}| MEMORY: {round(process.memory_info().rss / 1024 / 1024, 2)} MB\n')


if __name__ == '__main__':
    plot(Path('../../log/memory_server.txt'))
