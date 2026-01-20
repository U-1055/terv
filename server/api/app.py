import logging
import os

from flask import Flask, request
from sqlalchemy.orm.session import Session, sessionmaker

from pathlib import Path

from server.data_const import APIAnswers as APIAn
from server.auth.auth_module import Authenticator
from server.database.models.db_utils import launch_db
from server.database.repository import DataRepository
from server.storage.server_model import Model
from server.data_const import DataStruct, Config
from common.base import CommonStruct, check_password, ErrorCodes as ErCodes
from server.utils.data_checkers import check_email
from server.utils.api_utils import form_response, prepare_limit_offset
import server.api.crud_handlers as handlers
# ToDo: заголовок с Authorization на Authorization Bearer

logging.basicConfig(level=logging.WARN)
logging.debug('Module app.py is running')

app = Flask(__name__)
config = Config('../config.json')
database_path = config.database_path
engine = launch_db(database_path)

logging.debug(f'Module app.py is running. Environment: {config.env}')

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


@app.route('/register', methods=['POST'])
def register():
    login, password, email = request.json.get(common_struct.login), request.json.get(
        common_struct.password), request.json.get(common_struct.email)
    if not login:
        return form_response(400, APIAn.no_params_error(common_struct.login, request.endpoint))

    if len(login) < common_struct.min_login_length or len(
            login) > common_struct.max_login_length:  # Проверка длины логина
        return form_response(400,
                             APIAn.invalid_data_error(common_struct.login, request.endpoint,
                                                      ds_const.login_conditions), error_id=ErCodes.invalid_login.value
                             )

    if not password:
        return form_response(400, 
                             APIAn.no_params_error(
                                 common_struct.password, request.endpoint
                             ),
                             error_id=ErCodes.no_password.value
                             )
    if not check_password(password):
        return form_response(400,
                             APIAn.invalid_data_error(
                                 common_struct.password,
                                 request.endpoint, 
                                 ds_const.password_conditions
                             ),
                             error_id=ErCodes.invalid_password.value
                             )
    if not email:
        return form_response(400, 
                             APIAn.no_params_error(common_struct.email, request.endpoint),
                             error_id=ErCodes.no_email.value
                             )
    if not check_email(email):
        return form_response(400, 
                             APIAn.invalid_data_error(
                                 common_struct.email,
                                 request.endpoint, 
                                 "This email doesn't exist."),
                             error_id=ErCodes.invalid_email.value
                             )

    try:
        authenticator.register(login, email, password)
        return form_response(200, 'OK', {})
    except ValueError:
        by_login = repo.get_users_by_username((login, ))
        if by_login.content:  # Если есть пользователь с таким же логинов
            return form_response(400, 
                                 APIAn.invalid_data_error(
                                     common_struct.login,
                                     request.endpoint,
                                     f'That user ({login}) already exists'
                                 ),
                                 error_id=ErCodes.existing_login.value
                                 )
        by_email = repo.get_users_by_email(emails=email)
        if by_email.content:  # Если есть пользователь с таким же email'ом
            return form_response(400,
                                 APIAn.invalid_data_error(
                                     common_struct.login,
                                     request.endpoint, 
                                     f'User with this email already exists'),
                                 error_id=ErCodes.existing_email.value
                                 )
        return form_response(500, 'Unknown error during registration', error_id=ErCodes.server_error.value)  # Все параметры уникальны, но регистрация не удалась


@app.route('/auth/login', methods=['POST'])
def auth_login():
    login, password = request.json.get(common_struct.login), request.json.get(common_struct.password)
    if not login:
        return form_response(400,
                             APIAn.no_params_error(common_struct.login, request.endpoint),
                             error_id=ErCodes.no_login.value)
    if not password:
        return form_response(400,
                             APIAn.no_params_error(common_struct.password, request.endpoint),
                             error_id=ErCodes.no_password.value)
    try:
        tokens = authenticator.authorize(login, password)
        return form_response(200, 'OK', tokens)
    except ValueError:
        return form_response(400, APIAn.unknown_credentials_message, error_id=ErCodes.invalid_credentials.value)


@app.route('/auth/refresh', methods=['POST'])
def auth_refresh():
    refresh_token = request.json.get(common_struct.refresh_token)
    if not refresh_token:
        return form_response(400, APIAn.no_params_error(common_struct.refresh_token, request.endpoint), error_id=ErCodes.no_refresh.value)
    try:
        tokens = authenticator.update_tokens(refresh_token)
        return form_response(200, 'OK', tokens)
    except ValueError:
        return form_response(400, APIAn.invalid_data_error(common_struct.refresh_token, request.endpoint,
                                                           'Invalid refresh'), error_id=ErCodes.invalid_refresh.value)


@app.route('/auth/recall', methods=['POST'])
def auth_recall():
    """Отзывает переданные токены."""
    auth = request.headers.get('Authorization')
    if not authenticator.check_token_valid(auth, DataStruct.access_token):
        return form_response(401, 'Expired access token', error_id=ErCodes.invalid_access.value)

    params = request.json
    tokens = params.get(common_struct.tokens)
    if tokens:
        authenticator.recall_tokens(tokens)
    else:
        return form_response(400, 'No tokens', error_id=ErCodes.no_tokens.value)
    return form_response(200, 'OK')


@app.route('/personal_tasks', methods=['GET', 'POST', 'PUT', 'DELETE'])
def personal_tasks():
    auth = request.headers.get('Authorization')
    if not authenticator.check_token_valid(auth, DataStruct.access_token):
        return form_response(401, 'Expired access token', error_id=ErCodes.invalid_access.value)

    response = None  # Только чтобы не ругалась IDE на возможное отсутствие объявления

    if request.method == 'GET':
        response = handlers.get_wf_tasks(request, repo)
    elif request.method == 'POST':
        response = handlers.add_wf_tasks(request, repo)
    elif request.method == 'PUT':
        response = handlers.update_wf_tasks(request, repo)
    elif request.method == 'DELETE':
        response = handlers.update_wf_tasks(request, repo)

    return response


@app.route('/personal_tasks/search', methods=['POST'])
def personal_tasks_search():
    """Запрос для поиска по параметрам."""
    auth = request.headers.get('Authorization')
    if not authenticator.check_token_valid(auth, DataStruct.access_token):
        return form_response(401, 'Expired access token', error_id=ErCodes.invalid_access.value)
    return handlers.search_wf_tasks(request, repo)


@app.route('/users', methods=['GET', 'PUT', 'DELETE'])
def users():
    auth = request.headers.get('Authorization')

    if not authenticator.check_token_valid(auth, DataStruct.access_token):
        return form_response(401, 'Expired access token', error_id=ErCodes.invalid_access.value)

    response = None

    if request.method == 'GET':
        response = handlers.get_users(request, repo, authenticator)
    elif request.method == 'PUT':
        response = handlers.update_users(request, repo)
    elif request.method == 'DELETE':
        response = handlers.update_users(request, repo)

    return response


@app.route('/wf_tasks', methods=['GET', 'PUT', 'POST', 'DELETE'])
def wf_tasks():
    """
    Ресурс задач РП. Запроса вида: server://wf_tasks
    """

    auth = request.headers.get('Authorization')
    if not authenticator.check_token_valid(auth, DataStruct.access_token):
        return form_response(401, 'Expired access token', error_id=ErCodes.invalid_access.value)

    response = None

    if request.method == 'GET':
        response = handlers.get_wf_tasks(request, repo)
    elif request.method == 'POST':
        response = handlers.add_wf_tasks(request, repo)
    elif request.method == 'PUT':
        response = handlers.update_wf_tasks(request, repo)
    elif request.method == 'DELETE':
        response = handlers.update_wf_tasks(request, repo)

    return response


@app.route('/wf_tasks/search', methods=['POST'])
def wf_tasks_search():
    auth = request.headers.get('Authorization')
    if not authenticator.check_token_valid(auth, DataStruct.access_token):
        return form_response(401, 'Expired access token', error_id=ErCodes.invalid_access.value)

    return handlers.search_wf_tasks(request, repo)


def run():
    app.run()


def launch():
    import threading
    thread = threading.Thread(target=run)
    thread.start()


if __name__ == '__main__':
    launch()
