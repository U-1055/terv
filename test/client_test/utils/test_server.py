"""Сервер для тестов."""
import sys
import threading

from flask import Flask, request, Request, Response
from common.base import ErrorCodes, CommonStruct
from server.utils.api_utils import form_response
from test.client_test.utils.test_server_utils import TestRepo

app = Flask(__name__)
thread: threading.Thread | None = None
db_path: str | None = None
repo = TestRepo()


@app.route('/error/<int:err_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def error(err_id: int):
    return form_response(200, error_id=err_id, message='')


@app.route('/users', methods=['GET', 'POST', 'PUT', 'DELETE'])
def users():
    return form_response(400, error_id=2, message='1')


@app.route('/wf_tasks', methods=['GET'])
def wf_tasks():
    limit = request.args.get(CommonStruct.limit)
    offset = request.args.get(CommonStruct.offset)

    answer = repo.get_content(int(limit), int(offset))
    return form_response(200, 'OK', content=answer.get(repo.CONTENT), last_rec_num=answer.get(repo.LAST_REC_NUM),
                         records_left=answer.get(repo.RECORDS_LEFT))


def launch():
    global thread

    thread = threading.Thread(target=app.run)
    thread.start()


if __name__ == '__main__':
    launch()
