"""Основной файл сервера. Содержит слой роутеров."""
from flask import Flask, request
from sqlalchemy.orm.session import sessionmaker

from pathlib import Path

from common_utils.log_utils.memory_logger import check_memory
from server.data_const import APIAnswers as APIAn
from server.auth.auth_module import Authenticator, Authorizer
from server.database.models.db_utils import launch_db, init_db
from server.database.repository import DataRepository
from server.storage.server_model import Model
from server.data_const import DataStruct, Config, Permissions
from common.base import CommonStruct, check_password, ErrorCodes as ErCodes, DBFields
from common.logger import config_logger, SERVER
from server.api.base import LOG_DIR, MAX_FILE_SIZE, MAX_BACKUP_FILES, LOGGING_LEVEL
from server.utils.data_checkers import check_email
from server.utils.api_utils import form_response, exceptions_handler, form_success_response
import server.api.controllers.controllers as handlers


logger = config_logger(__name__, SERVER, LOG_DIR, MAX_BACKUP_FILES, MAX_FILE_SIZE, LOGGING_LEVEL)

app = Flask(__name__)
config = Config('../config.json')
database_path = config.database_path
engine = launch_db(database_path)

logger.info(f'Module is running. Environment: {config.env}. DB path: {database_path}.'
            f'Access lifetime: {config.access_token_lifetime}. Refresh lifetime: {config.refresh_token_lifetime}')

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
authorizer = Authorizer(
    repo,
    ds_const,
    Permissions
)

EXCLUDED_ENDPOINTS = ['register', 'auth_login', 'auth_refresh', 'auth_recall']


@app.before_request
def check_auth():
    if request.endpoint in EXCLUDED_ENDPOINTS:
        return

    auth = request.headers.get('Authorization')
    if not authenticator.check_token_valid(auth, DataStruct.access_token):
        return form_response(401, 'Expired access token', error_id=ErCodes.invalid_access.value)


@exceptions_handler
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
        by_email = repo.get_users_by_email(emails=[email])
        if by_email.content:  # Если есть пользователь с таким же email'ом
            return form_response(400,
                                 APIAn.invalid_data_error(
                                     common_struct.login,
                                     request.endpoint, 
                                     f'User with this email already exists'),
                                 error_id=ErCodes.existing_email.value
                                 )
        return form_response(500, 'Unknown error during registration', error_id=ErCodes.server_error.value)  # Все параметры уникальны, но регистрация не удалась


@exceptions_handler
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


@exceptions_handler
@app.route('/auth/refresh', methods=['POST'])
def auth_refresh():
    refresh_token = request.json.get(CommonStruct.refresh_token)
    if not refresh_token:
        return form_response(400, APIAn.no_params_error(common_struct.refresh_token, request.endpoint), error_id=ErCodes.no_refresh.value)
    try:
        tokens = authenticator.update_tokens(refresh_token)
        return form_response(200, 'OK', tokens)
    except ValueError:
        return form_response(400, APIAn.invalid_data_error(common_struct.refresh_token, request.endpoint,
                                                           'Invalid refresh'), error_id=ErCodes.invalid_refresh.value)


@exceptions_handler
@app.route('/auth/recall', methods=['POST'])
def auth_recall():
    """Отзывает переданные токены."""

    params = request.json
    tokens = params.get(common_struct.tokens)
    if tokens:
        authenticator.recall_tokens(tokens)
    else:
        return form_response(400, 'No tokens', error_id=ErCodes.no_tokens.value)
    return form_response(200, 'OK')


@exceptions_handler
@app.route('/personal_tasks', methods=['GET', 'POST', 'PUT', 'DELETE'])
def personal_tasks():

    response = None  # Только чтобы не ругалась IDE на возможное отсутствие объявления

    if request.method == 'GET':
        response = handlers.PersonalTaskController.get(request, repo)
    elif request.method == 'POST':
        response = handlers.PersonalTaskController.add(request, repo)
    elif request.method == 'PUT':
        response = handlers.PersonalTaskController.update(request, repo)
    elif request.method == 'DELETE':
        response = handlers.PersonalTaskController.delete(request, repo)

    return response


@exceptions_handler
@app.route('/personal_tasks/<int:task_id>/status', methods=['PUT'])
def personal_task_status(task_id: int):

    access_token = request.headers.get('Authorization')
    request_sender_id = authenticator.get_user_id(access_token)

    response = handlers.PersonalTaskController.change_status(request, task_id, repo)

    return response


@exceptions_handler
@app.route('/users', methods=['GET', 'PUT', 'DELETE'])
def users():

    response = None

    if request.method == 'GET':
        response = handlers.UserController.get(request, repo, authenticator)
    elif request.method == 'PUT':
        response = handlers.UserController.update(request, repo)
    elif request.method == 'DELETE':
        response = handlers.UserController.delete(request, repo)

    return response


@exceptions_handler
@app.route('/users/<int:user_id>/personal_tasks', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user_personal_tasks(user_id: int):
    response = None

    request_sender_id = authenticator.get_user_id(request.headers.get('Authorization'))
    if not authorizer.pre_check_access_to_personal_objects(request_sender_id, user_id):
        return form_response(403, f"You haven't access to personal objects of user (ID: {user_id})",
                             error_id=ErCodes.forbidden_access_to_personal_object.value)

    if request.method == 'GET':
        response = handlers.PersonalTaskController.get(request, repo, user_id)
    elif request.method == 'PUT':
        response = handlers.PersonalTaskController.update(request, repo)
    elif request.method == 'POST':
        response = handlers.PersonalTaskController.add(request, repo)
    elif request.method == 'DELETE':
        response = handlers.PersonalTaskController.delete(request, repo)

    return response


@exceptions_handler
@app.route('/users/<int:user_id>/ws_tasks', methods=['GET'])  # ToDo: удалить, перенести на основной эндпоинт получения задач
def user_ws_tasks(user_id: int):

    request_sender_id = authenticator.get_user_id(request.headers.get('Authorization'))
    if not authorizer.pre_check_access_to_personal_objects(request_sender_id, user_id):
        return form_response(403, f"You haven't access to personal objects of user (ID: {user_id})",
                             error_id=ErCodes.forbidden_access_to_personal_object.value)

    response = handlers.WSTaskController.get(request, repo, user_id)

    return response


@exceptions_handler
@app.route('/ws_tasks', methods=['GET', 'PUT', 'POST', 'DELETE'])
def ws_tasks():
    """
    Ресурс задач РП. Запроса вида: server://ws_tasks
    """

    response = None

    if request.method == 'GET':
        response = handlers.WSTaskController.get(request, repo)
    elif request.method == 'POST':
        response = handlers.WSTaskController.add(request, repo)
    elif request.method == 'PUT':
        response = handlers.WSTaskController.update(request, repo)
    elif request.method == 'DELETE':
        response = handlers.WSTaskController.delete(request, repo)

    return response


@exceptions_handler
@app.route('/ws_tasks/<int:task_id>/status', methods=['PUT'])
def ws_task_status(task_id: int):
    response = handlers.WSTaskController.change_status(request, task_id, repo)
    return response


@exceptions_handler
@app.route('/workspace/<int:workspace_id>/users', methods=['DELETE', 'POST', 'GET'])
def workspace_users(workspace_id: int):  # ToDo: протестировать
    response = None

    if request.method == 'POST':
        response = handlers.WorkspaceController.add(request, repo)
    if request.method == 'DELETE':
        response = handlers.WorkspaceController.delete(request, repo)
    if request.method == 'GET':
        request.args.update({DBFields.workspace_id: workspace_id})  # Не заработает, ToDo: убрать
        response = handlers.UserController.get(request, repo, authenticator)

    return response


@exceptions_handler
@app.route('/workspaces/<int:workspace_id>/ws_daily_events', methods=['PUT', 'GET', 'DELETE', 'POST'])
def ws_daily_events(workspace_id: int):
    response = None

    if request.method == 'GET':
        response = handlers.WSDailyEventController.get(request, repo)
    if request.method == 'POST':
        response = handlers.WSDailyEventController.add(request, workspace_id, repo)
    if request.method == 'PUT':
        response = handlers.WSDailyEventController.update(request, workspace_id, repo)
    if request.method == 'DELETE':
        pass

    return response


@exceptions_handler
@app.route('/workspaces/<int:workspace_id>/ws_many_days_events', methods=['PUT', 'GET', 'DELETE', 'POST'])
def ws_many_days_events(workspace_id: int):
    response = None

    if request.method == 'GET':
        response = handlers.WSManyDaysEventController.get(request, repo)
    if request.method == 'POST':
        response = handlers.WSDailyEventController.add(request, workspace_id, repo)
    if request.method == 'PUT':
        response = handlers.WSDailyEventController.update(request, workspace_id, repo)
    if request.method == 'DELETE':
        pass

    return response


@exceptions_handler
@app.route('/users/<int:user_id>/ws_many_days_events', methods=['GET'])
def user_ws_many_days_events(user_id: int):
    """Метод для получения многодневных событий, в которых участвует пользователь."""
    response = None

    if request.method == 'GET':
        response = handlers.WSManyDaysEventController.get(request, repo, user_id)

    return response


@exceptions_handler
@app.route('/users/<int:user_id>/ws_daily_events', methods=['GET'])
def user_ws_daily_events(user_id: int):
    """Метод для получения однодневных событий, в которых участвует пользователь."""
    response = None

    if request.method == 'GET':
        response = handlers.WSDailyEventController.get(request, repo, user_id=user_id)

    return response


@exceptions_handler
@app.route('/personal_daily_events', methods=['PUT', 'GET', 'DELETE', 'POST'])
def personal_daily_events():  # С фильтрацией по user_id и дате
    """Ресурс личных однодневных событий."""
    response = None

    if request.method == 'GET':
        response = handlers.PersonalDailyEventController.get(request, repo)

    return response


@exceptions_handler
@app.route('/personal_many_days_events', methods=['GET', 'POST', 'PUT', 'DELETE'])
def personal_many_days_events():
    """Ресурс личных многодневных событий."""
    response = None

    if request.method == 'GET':
        response = handlers.PersonalManyDaysEventController.get(request, repo)

    return response


@exceptions_handler
@app.route('/personal_task_events', methods=['GET', 'POST', 'PUT', 'DELETE'])
def personal_task_events():
    """Ресурс личных задачи-мероприятий."""
    response = None

    if request.method == 'GET':
        response = handlers.PersonalTaskEventController.get(request, repo)

    return response


@exceptions_handler
@app.route('/ws_task_events', methods=['GET', 'POST', 'PUT', 'DELETE'])
def ws_task_events():
    """Ресурс личных задачи-мероприятий."""
    # ToDo: фильтрация по статусам
    response = None

    if request.method == 'GET':
        response = handlers.WSTaskEventController.get(request, repo)

    return response


@exceptions_handler
@app.route('/users/search', methods=['GET'])
def users_search():
    """Поиск пользователей."""
    response = handlers.UserController.search(request, repo)
    return response


def run():
    app.run()


def launch(check_ram: bool = False):
    import threading
    if check_ram:
        thread = threading.Thread(target=check_memory, args=[Path('../../log/memory_server.txt')], daemon=True)
        thread.start()

    thread = threading.Thread(target=run)
    thread.start()


if __name__ == '__main__':
    launch(True)
