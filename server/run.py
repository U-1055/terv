"""Файл запуска сервера в производственном окружении."""
from waitress import serve

import threading
import os
from pathlib import Path

from common_utils.log_utils.memory_logger import check_memory
os.chdir('api')
from server.api.app import app


serve(app, host='127.0.0.1', port=8080, threads=8)

thread = threading.Thread(target=check_memory, args=[Path('../../log/memory_server.txt')], daemon=True)
thread.start()

