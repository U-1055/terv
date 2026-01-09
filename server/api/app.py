import logging

from flask import Flask, request, jsonify, Request, Response
from sqlalchemy.orm.session import Session, sessionmaker
from sqlalchemy.engine import create_engine, Engine

from pathlib import Path
import typing as tp

from server.data_const import APIAnswers as APIAn
from server.auth.auth_module import Authenticator
from server.database.models.base import launch_db, init_db, Base, config_db
from server.database.repository import DataRepository
from server.storage.server_model import Model
from server.data_const import DataStruct, Config
from common.base import DataStruct as CommonStruct
# ToDo: проверка уникальности параметров пользователя
logging.basicConfig(level=logging.DEBUG)
logging.debug('Module app.py is running')

app = Flask(__name__)
config = Config(Path('../config.json'))
print(config.env)
if config.env == DataStruct.test:  # В тестовом окружении БД инициализируется заново
    engine = init_db('sqlite:///../database/database')
else:
    engine = launch_db('sqlite:///../database/database')

session = sessionmaker(bind=engine)
repo = DataRepository(session)
model = Model(Path('../storage/storage'))
ds_const = DataStruct()

common_struct = CommonStruct()

authenticator = Authenticator(
    repo,
    model,
    ds_const.jwt_alg,
    config.access_token_lifetime,
    config.refresh_token_lifetime
)


def form_response(code: int, message: str, content: tp.Any = None) -> Response:
    response = {
        'message': message
    }
    if content:
        response.update(content=content)
    result = jsonify(response)
    result.status_code = code
    return result


@app.route('/register', methods=['POST'])
def register():
    login, password, email = request.json.get(common_struct.login), request.json.get(common_struct.password), request.json.get(common_struct.email)
    if not login:
        return form_response(400, APIAn.no_params_error(common_struct.login, request.endpoint))
    if not password:
        return form_response(400, APIAn.no_params_error(common_struct.password, request.endpoint))
    if not email:
        return form_response(400, APIAn.no_params_error(common_struct.email, request.endpoint))

    repo.add_users(
        ({
            ds_const.username: login,
            ds_const.email: email,
            ds_const.hashed_password: password
        },)
    )
    return form_response(200, 'OK', {})


@app.route('/auth/login', methods=['POST'])
def auth_login():
    login, password = request.json.get(common_struct.login), request.json.get(common_struct.password)
    if not login:
        return form_response(400, APIAn.no_params_error(common_struct.login, request.endpoint))
    if not password:
        return form_response(400, APIAn.no_params_error(common_struct.password, request.endpoint))
    try:
        tokens = authenticator.authorize(login, password)
        return form_response(200, 'OK', tokens)
    except ValueError:
        return form_response(400, APIAn.unknown_credentials_message)


@app.route('/auth/refresh', methods=['POST'])
def auth_refresh():

    refresh_token = request.json.get(common_struct.refresh_token)
    if not refresh_token:
        return form_response(400, APIAn.no_params_error(common_struct.refresh_token, request.endpoint))
    try:
        tokens = authenticator.update_tokens(refresh_token)
        return form_response(200, 'OK', tokens)
    except ValueError:
        return form_response(400, APIAn.invalid_data_error(common_struct.refresh_token, request.endpoint, APIAn.no_login_message))


@app.route('/personal_tasks', methods=['GET', 'POST', 'PUT', 'DELETE'])
def personal_tasks():
    """server://tasks?user&from_date&until_date"""
    params = request.json
    auth = request.headers.get('Authorization')
    if not authenticator.check_token_valid(auth):
        return form_response(401, 'Expired access token')


@app.route('/users', methods=['GET', 'PUT', 'DELETE'])
def users():
    auth = request.headers.get('Authorization')
    logins = request.json.get(common_struct.logins)

    if not authenticator.check_token_valid(auth):
        return form_response(401, 'Expired access token')

    if not logins:  # Если передан только
        try:
            logins = [authenticator.get_login(auth)]
        except ValueError:
            return form_response(401, 'Expired access token')

    users = repo.get_users(logins)

    return form_response(200, 'OK', content=users)


def run():
    app.run()


def launch():
    import threading
    thread = threading.Thread(target=run)
    thread.start()


if __name__ == '__main__':
    launch()
