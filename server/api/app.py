import logging

from flask import Flask, request, jsonify, Request, Response
from sqlalchemy.orm.session import Session, sessionmaker

from pathlib import Path
import typing as tp

import server.database.models.common_models as db
from server.data_const import APIAnswers as APIAn
from server.auth.auth_module import Authenticator
from server.database.models.base import launch_db, init_db
from server.database.repository import DataRepository
from server.storage.server_model import Model
from server.data_const import DataStruct

logging.basicConfig(level=logging.DEBUG)
logging.debug('Module app.py is running')

app = Flask(__name__)
engine = init_db()
session = sessionmaker(bind=engine)
repo = DataRepository(session)
model = Model(Path('../storage/storage'))
ds_const = DataStruct()

authenticator = Authenticator(
    repo,
    model,
    ds_const.jwt_alg,
    ds_const.access_token_lifetime,
    ds_const.refresh_token_lifetime
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
    login, password, email = request.json.get('login'), request.json.get('password'), request.json.get('email')
    if not login:
        return form_response(400, APIAn.no_params_error('login', request.endpoint))
    if not password:
        return form_response(400, APIAn.no_params_error('password', request.endpoint))
    if not email:
        return form_response(400, APIAn.no_params_error('email', request.endpoint))

    repo.add_users(
        ({
            ds_const.login: login,
            ds_const.email: email,
            ds_const.hashed_password: password
        },)
    )
    return form_response(200, 'OF', {})


@app.route('/auth/login', methods=['POST'])
def auth_login():
    login, password = request.json.get('login'), request.json.get('password')
    if not login:
        return form_response(400, APIAn.no_params_error('login', request.endpoint))
    if not password:
        return form_response(400, APIAn.no_params_error('password', request.endpoint))
    tokens = authenticator.authorize(login, password)
    if tokens:
        return form_response(200, 'OK', tokens)
    else:
        return form_response(400, APIAn.unknown_credentials_message)


@app.route('/auth/refresh', methods=['POST'])
def auth_refresh():

    refresh_token = request.json.get('refresh_token')
    if not refresh_token:
        return form_response(400, APIAn.no_params_error('refresh_token', request.endpoint))
    try:
        tokens = authenticator.update_tokens(refresh_token)
        return form_response(200, 'OK', tokens)
    except ValueError:
        return form_response(400, APIAn.invalid_data_error('refresh_token', request.endpoint, APIAn.no_login_message))


@app.route('/personal_tasks', methods=['GET', 'POST', 'PUT', 'DELETE'])
def personal_tasks():
    """server://tasks?user&from_date&until_date"""
    params = request.json
    auth = request.headers.get('Authorization')
    if not authenticator.check_token_valid(auth):
        return form_response(401, 'Expired access token')


@app.route('/users', methods=['GET', 'PUT', 'DELETE'])
def users():
    logins = request.args.getlist('logins')
    auth = request.headers.get('Authorization')
    if not authenticator.check_token_valid(auth):
        return form_response(401, 'Expired access token')

    if logins:
        users_data = repo.get_users(logins)
    else:
        login = authenticator.get_login(auth)
        users_data = repo.get_users((login, ))
    logging.debug(f'Userdata received: {users_data}')

    if users_data:
        logging.debug(f'Userdata received: {users_data}')
        return form_response(200, 'OK', users_data)
    else:
        return form_response(400, f'There is no user with this login: {logins}')


def run():
    app.run()


def launch():
    import threading
    thread = threading.Thread(target=run)
    thread.start()


if __name__ == '__main__':
    launch()
