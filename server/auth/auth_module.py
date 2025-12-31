import datetime
import logging
import shelve

import jwt
from bcrypt import checkpw, hashpw, gensalt

from server.storage.server_model import Model
from server.database.repository import DataRepository
from server.data_const import DataStruct, Permissions


def hash_password(password: str) -> str:
    return hashpw(bytes(password, encoding='utf-8'), gensalt()).decode('utf-8')


class Authenticator:
    """Класс, отвечающий за проверку аутентификации пользователя."""

    def __init__(
             self,
             repository: DataRepository,
             model: Model,
             jwt_alg: str,
             access_token_lifetime: datetime.timedelta,
             refresh_token_lifetime: datetime.timedelta,
             data_struct: DataStruct = DataStruct()
                 ):
        self._jwt_alg = jwt_alg
        self._repository = repository
        self._model = model
        self._access_token_lifetime = access_token_lifetime
        self._refresh_token_lifetime = refresh_token_lifetime
        self._data_struct = data_struct

    def _create_token(self, login: str, lifetime: datetime.timedelta) -> str:
        secret = self._model.get_secret()
        token_ = jwt.encode(
            payload={
                'login': login,
                'exp': datetime.datetime.now(tz=datetime.timezone.utc) + lifetime
            },
            key=secret,
            algorithm=self._jwt_alg
        )
        return token_

    def check_token_valid(self, token_: str) -> bool:
        """Проверяет валидность токена. Возвращает логическое значение <Токен валиден>"""
        secret = self._model.get_secret()
        if self._model.check_token_in_blacklist(token_):
            return False
        try:
            jwt.decode(token_, key=secret, algorithms=[self._jwt_alg])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return False
        return True

    def get_login(self, token_: str) -> str:
        if self.check_token_valid(token_):
            secret = self._model.get_secret()
            payload = jwt.decode(token_, key=secret, algorithms=[self._jwt_alg])
            return payload.get('login')

    def update_tokens(self, refresh_token: str) -> dict[str, str]:
        """Возвращает новую пару access + refresh по refresh-токену."""
        if self.check_token_valid(refresh_token):
            secret = self._model.get_secret()
            payload = jwt.decode(refresh_token, key=secret, algorithms=[self._jwt_alg])
            login = payload.get('login')
            if not login:
                raise ValueError('Invalid token: no login')
            access_token = self._create_token(login, self._access_token_lifetime)
            new_refresh_token = self._create_token(login, self._refresh_token_lifetime)

            self._model.add_token_to_blacklist(refresh_token)

            return {'access': access_token, 'refresh': new_refresh_token}
        else:
            raise ValueError

    def register(self, login: str, email: str, password: str):
        hashed_password = hash_password(password)
        self._repository.add_users(({'username': login, 'email': email, 'hashed_password': hashed_password},))

    def recall_tokens(self, tokens: list):
        """Добавляет полученные токены в blacklist."""
        for token_ in tokens:
            self._model.add_token_to_blacklist(token_)

    def authorize(self, login: str, password: str) -> dict[str, str]:
        """Авторизует пользователя. Возвращает пару access + refresh JWT-токенов."""
        result = self._repository.get_users((login, ))[0]
        if result['username'] == login:
            try:
                checkpw(bytes(password, encoding='utf-8'), bytes(result['hashed_password'], encoding='utf-8'))
                access_token = self._create_token(login, self._access_token_lifetime)
                refresh_token = self._create_token(login, self._refresh_token_lifetime)
                return {self.access_name: access_token, self.refresh_name: refresh_token}
            except ValueError:
                logging.debug(f'INVALID PASSWORD: saved_hash: {result['hashed_password']}; received_hash: {bytes(password, encoding='utf-8')}')

    @property
    def access_name(self):
        return self._data_struct.access

    @property
    def refresh_name(self):
        return self._data_struct.refresh


class Authorizer:
    """Проверяет роль пользователя."""
    def __init__(self, repository: DataRepository, data_const: DataStruct = DataStruct(), permissions: Permissions = Permissions):
        self._repo = repository
        self._data_const = data_const
        self._permissions = permissions

    def check_permissions(self, user_role_id: int, object_id: int, object_type: str, permission: str) -> bool:
        """
        Проверяет доступ пользователя к ресурсу.
        :param user_role_id: id роли пользователя в РП.
        :param object_id: id объекта, к которому получает доступ пользователь.
        :param object_type: тип объекта (задача, проект, документ, однодневное мероприятие, многодневное мероприятие).
        :param permission: получаемый доступ.
        :return: наличие доступа
        """

        if permission not in self._permissions:
            raise ValueError(f'Unknown permission: {permission}')

        if object_type == self._data_const.task:
            permissions = self._repo.get_task_permissions(object_id, user_role_id)
        elif object_type == self._data_const.project:
            permissions = self._repo.get_project_permissions(object_id, user_role_id)
        elif object_type == self._data_const.document:
            permissions = self._repo.get_document_permissions(object_id, user_role_id)
        elif object_type == self._data_const.daily_event:
            permissions = self._repo.get_daily_event_permissions(object_id, user_role_id)
        elif object_type == self._data_const.many_days_event:
            permissions = self._repo.get_task_permissions(object_id, user_role_id)
        else:
            raise ValueError(f'Unknown object type: {object_type}')

        return permission in permissions


if __name__ == '__main__':
    from server.database.models.base import init_db, sessionmaker
    from pathlib import Path

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

    authenticator.register('log1', 'em1', 'pass1')
    print(authenticator.authorize('log1', 'pass1'))

