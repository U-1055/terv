import shelve
from pathlib import Path
import jwt
from server.data_const import DataStruct


class Model:

    def __init__(self, storage_path: Path, data_const: DataStruct = DataStruct()):
        self._storage_path = storage_path
        self._data_const = data_const

    def update_blacklist(self):
        """Удаляет из блек-листа токены с истёкшим временем жизни."""
        with shelve.open(self._storage_path, 'w') as storage:
            tokens = list(storage[self._data_const.blacklist])
            for token_ in tokens:
                try:
                    jwt.decode(token_)
                except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                    tokens.remove(token_)
            storage[self._data_const.blacklist] = tokens

    def get_secret(self) -> str:
        with shelve.open(self._storage_path) as storage:
            secret = storage.get(self._data_const.secret)
        return secret

    def add_token_to_blacklist(self, token_: str):
        with shelve.open(self._storage_path, 'w') as storage:
            tokens = storage[self._data_const.blacklist]
            if token_ not in tokens:
                tokens.append(token_)
            storage[self._data_const.blacklist] = tokens

    def delete_token_from_blacklist(self, token_: str):
        with shelve.open(self._storage_path, 'w') as storage:
            tokens = storage[self._data_const.blacklist]
            tokens.remove(token_)
            storage[self._data_const.blacklist] = tokens

    def check_token_in_blacklist(self, token_: str) -> bool:
        """Проверяет наличие токена в блеклисте."""
        with shelve.open(self._storage_path) as storage:
            tokens = storage[self._data_const.blacklist]
            return token_ in tokens


if __name__ == '__main__':
    model = Model(Path('storage'))
    print(model.get_secret())

    model.update_blacklist()
    model.add_token_to_blacklist('12345')
    model.add_token_to_blacklist('12345')
    model.add_token_to_blacklist('12345')
    model.delete_token_from_blacklist('12345')
    print(model.check_token_in_blacklist('12345'))
