import os
import re
import uuid
from dotenv import load_dotenv
from hashlib import sha256
from typing import Optional

from domain.interfaces.repositories.i_user_repository import IUserRepository
from domain.interfaces.services.i_user_service import IUserService
from domain.models.user import User
from domain.models.userLogin import UserLogin
from domain.models.userSignup import UserSignup

load_dotenv()


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
        pepper = os.getenv("PEPPER")
        hashed_password = sha256((user.password + pepper).encode('utf-8'))
        user.password = hashed_password.hexdigest()
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


    def login_user(self, user: UserLogin) -> Optional[str]:
        user_exists: User
        if "@" in user.identifier:
            user_exists = self.get_user_by_email(user.identifier)
        else:
            user_exists = self.get_user_by_username(user.identifier)

        if user_exists is None:
            return "Utilisateur non trouvé"

        salted_password = sha256((user.password + user_exists.salt).encode('utf-8'))

        pepper = os.getenv("PEPPER")
        hashed_password = sha256((salted_password.hexdigest() + pepper).encode('utf-8'))

        if hashed_password.hexdigest() == user_exists.password:
            return user_exists.id
        else:
            return "Mot de passe incorrect"