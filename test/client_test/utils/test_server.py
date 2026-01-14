"""Сервер для тестов."""
import sys
import threading

from flask import Flask, request, Request, Response
from common.base import ErrorCodes
from server.utils.api_utils import form_response

app = Flask(__name__)
thread: threading.Thread | None = None


@app.route('/error/<int:err_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def error(err_id: int):
    print(ErrorCodes.no_password.value == err_id)
    return form_response(200, error_id=err_id, message='')


@app.route('/users', methods=['GET', 'POST', 'PUT', 'DELETE'])
def users():
    return form_response(400, error_id=2, message='1')


def launch():
    global thread
    thread = threading.Thread(target=app.run)
    thread.start()


if __name__ == '__main__':
    launch()
