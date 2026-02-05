from sqlalchemy.exc import IntegrityError

import datetime
import logging
import enum
import os
import shelve
import jwt
from bcrypt import checkpw, hashpw, gensalt

from server.storage.server_model import Model
from server.database.repository import DataRepository
from server.data_const import DataStruct, Permissions
from common.base import DBFields, CommonStruct
from server.database.models.base import Base


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
        self._model.get_secret()
        self._access_token_lifetime = access_token_lifetime
        self._refresh_token_lifetime = refresh_token_lifetime
        self._data_struct = data_struct

    def _create_token(self, user_id: int, lifetime: datetime.timedelta) -> str:
        secret = self._model.get_secret()
        token_ = jwt.encode(
            payload={
                'sub': str(user_id),
                'exp': datetime.datetime.now(tz=datetime.timezone.utc) + lifetime,  # Время истечения токена
                'iat': datetime.datetime.now(tz=datetime.timezone.utc)  # Время создания токена
            },
            key=secret,
            algorithm=self._jwt_alg
        )
        return token_

    def check_token_valid(self, token_: str, type_: str) -> bool:
        """
        Проверяет валидность токена. Возвращает логическое значение <Токен валиден>
        :param token_: токен
        :param type_: тип токена (access_token или refresh_token)
        """

        secret = self._model.get_secret()
        if self._model.check_token_in_blacklist(token_):
            return False
        try:
            payload = jwt.decode(token_, key=secret, algorithms=[self._jwt_alg])
            creating_time = payload.get('iat')  # Проверка типа токена
            expiring_time = payload.get('exp')
            if type_ == self._data_struct.access_token:
                if expiring_time - creating_time != self._access_token_lifetime.seconds:
                    return False
            elif type_ == self._data_struct.refresh_token:
                if expiring_time - creating_time != self._refresh_token_lifetime.seconds:
                    assert ValueError(f'Refresh-Token expired: {expiring_time}')
                    return False
            else:
                raise ValueError(f'Unknown token_type: {type_}. Must be access or refresh')

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return False
        return True

    def get_user_id(self, token_: str) -> int:
        """
        Возвращает user_id из access-токена. Вызывает ValueError, если токен недействителен или произошла ошибка при
        декодировании.
        """
        if self.check_token_valid(token_, self._data_struct.access_token):
            secret = self._model.get_secret()
            payload = jwt.decode(token_, key=secret, algorithms=[self._jwt_alg])
            return payload.get('sub')
        else:
            raise ValueError

    def update_tokens(self, refresh_token: str) -> dict[str, str]:
        """
        Возвращает новую пару access + refresh по refresh-токену.
        Вызывает ValueError, если токен недействителен или произошла ошибка при
        декодировании.
        """

        if self.check_token_valid(refresh_token, self._data_struct.refresh_token):
            secret = self._model.get_secret()
            payload = jwt.decode(refresh_token, key=secret, algorithms=[self._jwt_alg])
            user_id = payload.get('sub')

            if not user_id:
                raise ValueError('Invalid token: no user_id')
            access_token = self._create_token(user_id, self._access_token_lifetime)
            new_refresh_token = self._create_token(user_id, self._refresh_token_lifetime)

            self._model.add_token_to_blacklist(refresh_token)

            return {'access': access_token, 'refresh': new_refresh_token}
        else:
            raise ValueError

    def register(self, login: str, email: str, password: str):
        hashed_password = hash_password(password)
        try:
            self._repository.add_users(({DBFields.username: login, DBFields.email: email, DBFields.hashed_password: hashed_password},))
        except IntegrityError:
            raise ValueError

    def recall_tokens(self, tokens: list):
        """Добавляет полученные токены в blacklist."""
        for token_ in tokens:
            self._model.add_token_to_blacklist(token_)

    def authorize(self, login: str, password: str) -> dict[str, str]:
        """
        Авторизует пользователя. Возвращает пару access + refresh JWT-токенов.
        Вызывает ValueError, если авторизация не удалась.
        """

        user_data = self._repository.get_users_by_username((login, ))

        if not user_data or not user_data.content:
            raise ValueError
        hashed_password = self._repository.get_user_hashed_password(login)
        user_id = user_data.content[0].get(DBFields.id)

        try:
            if not checkpw(bytes(password, encoding='utf-8'), bytes(hashed_password, encoding='utf-8')):
                raise ValueError
            access_token = self._create_token(user_id, self._access_token_lifetime)
            refresh_token = self._create_token(user_id, self._refresh_token_lifetime)
            return {self.access_name: access_token, self.refresh_name: refresh_token}
        except ValueError as e:
            logging.debug(f'INVALID PASSWORD: saved_hash: {hashed_password}; received_hash: {bytes(password, encoding='utf-8')}')
            raise ValueError

    @property
    def access_name(self):
        return self._data_struct.access_token

    @property
    def refresh_name(self):
        return self._data_struct.refresh_token


class Authorizer:
    """Проверяет роль пользователя."""
    def __init__(self, repository: DataRepository, data_const: DataStruct = DataStruct(), permissions: enum.Enum = Permissions):
        self._repo = repository
        self._data_const = data_const
        self._permissions = permissions

    @staticmethod
    def check_access_to_personal_objects(user_id: int, objects: list[dict]) -> bool:
        """
        Проверяет доступ пользователя к личным объектам.
        Если нет доступа хотя бы к одному из объектов - возвращает False.
        """

        for object_ in objects:
            owner_id = object_.get(DBFields.owner_id)
            if owner_id != user_id:
                return False
        return True

    @staticmethod
    def pre_check_access_to_personal_objects(user_id: int, owner_id: int) -> bool:
        """Проверяет доступ пользователя к личным объектам."""
        return user_id == owner_id

    def check_permissions(self, user_id: int, objects: list[dict], object_type: str, permission: str) -> bool:
        """
        Проверяет доступ пользователя к ресурсу.
        :param user_id: ID пользователя, который делает запрос.
        :param objects: сериализованные модели, к которым нужно получить доступ.
        :param object_type: тип объекта (задача, проект, документ, однодневное мероприятие, многодневное мероприятие).
        :param permission: получаемый доступ.
        :return: наличие доступа
        """

        if permission not in self._permissions:
            raise ValueError(f'Unknown permission: {permission}')
        workflows_ids = []
        for object_ in objects:
            id_ = object_.get(DBFields.workflow_id)
            if not id_:
                raise ValueError(f'The serialized model have not field "workflow_id". Model: {object_}')

        for id_ in workflows_ids:  # Временная схема
            role_id = self._repo.get_role_by_user_id(id_, user_id).content
            if not role_id:
                return False  # Нет роли - значит пользователя нет в РП
            for object_ in objects:
                object_id = object_.get(DBFields.id)
                if object_type == self._data_const.task:
                    permissions = self._repo.get_task_permissions(object_id, role_id)
                elif object_type == self._data_const.project:
                    permissions = self._repo.get_project_permissions(object_id, role_id)
                elif object_type == self._data_const.document:
                    permissions = self._repo.get_document_permissions(object_id, role_id)
                elif object_type == self._data_const.daily_event:
                    permissions = self._repo.get_daily_event_permissions(object_id, role_id)
                elif object_type == self._data_const.many_days_event:
                    permissions = self._repo.get_task_permissions(object_id, role_id)
                else:
                    raise ValueError(f'Unknown object type: {object_type}')
                return permission in permissions


if __name__ == '__main__':
    from server.database.models.base import init_db, sessionmaker
    from pathlib import Path

    engine = init_db('sqlite:///../database/database')
    session = sessionmaker(bind=engine)
    repo = DataRepository(session)
    model = Model(Path('../storage/storage'))
    ds_const = DataStruct()

    authenticator = Authenticator(
        repo,
        model,
        ds_const.jwt_alg,
        ds_const.default_access_token_lifetime,
        ds_const.default_refresh_token_lifetime
    )

    authenticator.register('log1', 'em1', 'pass1')
