from client.src.requester.requester import Requester
from client.models.common_models import User


class TestRequester(Requester):

    def __init__(self, server: str):
        super().__init__('')

    def register(self, login: str, password: str, email: str):
        pass

    def update_tokens(self, refresh_token: str) -> dict:
        pass

    def authorize(self, login: str, password: str) -> dict:
        pass

    def get_user_info(self, access_token: str):
        user = User()
        user.id = 0
        user.username = 'sth'
        user.hashed_password = 'sth'
        user.email = 'sth'
        return user

    def get_personal_tasks(self, user_id: int, access_token: str):
        pass
