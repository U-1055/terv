import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


CLIENT = 'client'
SERVER = 'server'


def format_log_file_name(number: int, type_: str) -> str:
    """Возвращает имя файла логов в формате: log_<type_ (client/server)>_<number>.txt"""
    return f'log_{type_}_{number}.txt'


def get_full_files_count(dir_: Path, full_file_size: int) -> int:
    full_files = 0
    for file in dir_.iterdir():
        if file.stat().st_size >= full_file_size:
            full_files += 1
    return full_files


def config_logger(module: str, type_: str, log_dir: Path, backup_files_count: int = 25,
                  max_file_size: int = 10 * 1024, logging_level: int = logging.INFO) -> logging.Logger:
    """
    Настраивает логгер.

    :param module: Название модуля.
    :param type_: Тип (клиент или сервер)
    :param log_dir: Путь pathlib.Path к папке с файлами логов.
    :param backup_files_count: Максимальное число файлов логов.
    :param max_file_size: Максимальный размер файла логов (по умолчанию - 10 КБ).
    :param logging_level: Уровень логирования. DEBUG - INFO - WARNING - ERROR - CRITICAL

    """

    logger = logging.getLogger(module)
    logger.setLevel(logging_level)

    if log_dir.is_dir():
        files_count = get_full_files_count(log_dir, max_file_size)
        log_file = Path(log_dir, format_log_file_name(files_count + 1, type_))
        formatter = logging.Formatter(f"{module} - [%(asctime)s] - %(levelname)s - MSG: %(message)s")
        file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024, backupCount=backup_files_count)  # 10 КБ
        file_handler.setFormatter(formatter)
    else:
        logging.basicConfig(level=logging.INFO)
        logging.error(f'There is no dir in: {log_dir}')
        print(f'ERROR: There is no dir in: {log_dir}')

    return logger
