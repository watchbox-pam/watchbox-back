import re
import uuid
from typing import Optional

from domain.interfaces.repositories.i_user_repository import IUserRepository
from domain.interfaces.services.i_user_service import IUserService
from domain.models.user import User
from domain.models.userSignup import UserSignup


class UserService(IUserService):
    def __init__(self, repository: IUserRepository):
        self.repository = repository

    def create_user(self, user: UserSignup) -> Optional[str]:

        username_exists = self.get_user_by_username(user.username)
        if username_exists is not None:
            return "Ce pseudo est déjà utilisé"

        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if re.match(pattern, user.email) is None:
            return "Cette adresse mail n'est pas valide"

        email_exists = self.get_user_by_email(user.email)
        if email_exists is not None:
            return "Cette adresse mail est déjà utilisée"

        user_id: uuid = uuid.uuid4()
        user.id = str(user_id)
        if self.repository.create_user(user):
            return str(user_id)
        else:
            return ""


    def get_user_by_username(self, username: str) -> Optional[User]:
        user = self.repository.get_user_by_username(username)
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        user = self.repository.get_user_by_email(email)
        return user