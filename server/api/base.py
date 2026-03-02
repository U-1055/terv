"""Содержит пути к файлам, используется всеми остальными модулями сервера."""
from pathlib import Path
import logging

# Параметры логирования
LOG_DIR = Path('../log')
MAX_BACKUP_FILES = 20
MAX_FILE_SIZE = 100 * 1024
LOGGING_LEVEL = logging.INFO
