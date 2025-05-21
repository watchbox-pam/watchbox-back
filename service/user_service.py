import os
import re
import uuid
from dotenv import load_dotenv
from hashlib import sha256
from typing import Optional

from api.auth.verify_auth_token import create_jwt_token
from domain.interfaces.repositories.i_playlist_repository import IPlaylistRepository
from domain.interfaces.repositories.i_user_repository import IUserRepository
from domain.interfaces.services.i_user_service import IUserService
from domain.models.user import User
from domain.models.userLogin import UserLogin
from domain.models.userSignup import UserSignup

load_dotenv()


class UserService(IUserService):
    def __init__(self, repository: IUserRepository, playlist_repository: IPlaylistRepository):
        self.repository = repository
        self.playlist_repository = playlist_repository

    def create_user(self, user: UserSignup) -> dict[str, str]:

        username_exists = self.get_user_by_username(user.username)
        if username_exists is not None:
            raise Exception("Ce pseudo est déjà utilisé")

        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if re.match(pattern, user.email) is None:
            raise Exception("Cette adresse mail n'est pas valide")

        email_exists = self.get_user_by_email(user.email)
        if email_exists is not None:
            raise Exception("Cette adresse mail est déjà utilisée")

        user_id: uuid = uuid.uuid4()
        user.id = str(user_id)
        pepper = os.getenv("PEPPER")
        hashed_password = sha256((user.password + pepper).encode('utf-8'))
        user.password = hashed_password.hexdigest()
        if self.repository.create_user(user):
            self.playlist_repository.create_playlist_on_register(user_id=user.id)
            user_token = create_jwt_token({"user_id": str(user_id)})
            return { "user_id": str(user_id), "token": user_token }
        else:
            raise Exception("La création de l'utilisateur a échoué")

    def get_user_by_id(self, id: str) -> Optional[User]:
        user = self.repository.get_user_by_id(id)
        return user

    def get_user_by_username(self, username: str) -> Optional[User]:
        user = self.repository.get_user_by_username(username)
        return user


    def get_user_by_email(self, email: str) -> Optional[User]:
        user = self.repository.get_user_by_email(email)
        return user


    def login_user(self, user: UserLogin) -> dict[str, str]:
        user_exists: User
        if "@" in user.identifier:
            # Check if email exists in base
            user_exists = self.get_user_by_email(user.identifier)
        else:
            # Check if username exists in base
            user_exists = self.get_user_by_username(user.identifier)

        if user_exists is None:
            raise Exception("Utilisateur non trouvé")

        salted_password = sha256((user.password + user_exists.salt).encode('utf-8')).hexdigest()

        pepper = os.getenv("PEPPER")
        hashed_password = sha256((salted_password + pepper).encode('utf-8'))

        if hashed_password.hexdigest() == user_exists.password:
            user_token = create_jwt_token({ "user_id": str(user_exists.id) })
            return { "user_id": str(user_exists.id), "token": user_token, "username": user_exists.username }
        else:
            raise Exception("Mot de passe incorrect")