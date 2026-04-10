import os
import random
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
from domain.models.userPassword import UserPassword
from domain.models.userSignup import UserSignup
from domain.models.userVerification import UserVerification
from utils.mail_service import send_mail

load_dotenv()


class UserService(IUserService):
    def __init__(self, repository: IUserRepository, playlist_repository: IPlaylistRepository):
        self.repository = repository
        self.playlist_repository = playlist_repository

    def create_user(self, user: UserSignup) -> dict[str, str]:

        # Check if username is taken
        username_exists = self.get_user_by_username(user.username)
        if username_exists is not None:
            raise Exception("Ce pseudo est déjà utilisé")

        # Check if email address is valid
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if re.match(pattern, user.email) is None:
            raise Exception("Cette adresse mail n'est pas valide")

        # Check if email address is taken
        email_exists = self.get_user_by_email(user.email)
        if email_exists is not None:
            raise Exception("Cette adresse mail est déjà utilisée")

        # Generate user id
        user_id: uuid = uuid.uuid4()
        user.id = str(user_id)

        # Hash user password with pepper
        pepper = os.getenv("PEPPER")
        hashed_password = sha256((user.password + pepper).encode('utf-8'))
        user.password = hashed_password.hexdigest()

        # Generate verification code
        verification_code_int = random.randint(0, 999999)
        verification_code = "%06d" % verification_code_int

        # Generate verification code token
        verification_code_token_uuid = uuid.uuid4()
        hashed_verification_code_token = sha256(str(verification_code_token_uuid).encode('utf-8'))
        verification_code_token = hashed_verification_code_token.hexdigest()

        # Generate password reset token
        password_reset_token_uuid = uuid.uuid4()
        hashed_password_reset_token = sha256(str(password_reset_token_uuid).encode('utf-8'))
        password_reset_token = hashed_password_reset_token.hexdigest()

        if self.repository.create_user(user, password_reset_token, verification_code, verification_code_token):
            html = f"""\
            <b>Bonjour, {user.username}</b><br/>
            Votre code pour finaliser votre inscription à Watchbox est {verification_code}</a>
            """
            send_mail(user.email, "Vérification de votre compte Watchbox", html)
            self.playlist_repository.create_playlist_on_register(user_id=user.id)
            user_token = create_jwt_token({"user_id": str(user_id)})
            return { "user_id": str(user_id), "token": user_token, "verification_code_token": verification_code_token }
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

        if not user_exists.is_verified:
            raise Exception("Utilisateur non vérifié")

        salted_password = sha256((user.password + user_exists.salt).encode('utf-8')).hexdigest()

        pepper = os.getenv("PEPPER")
        hashed_password = sha256((salted_password + pepper).encode('utf-8'))

        if hashed_password.hexdigest() == user_exists.password:
            user_token = create_jwt_token({ "user_id": str(user_exists.id) })
            return { "user_id": str(user_exists.id), "token": user_token, "username": user_exists.username }
        else:
            raise Exception("Mot de passe incorrect")


    def verify_user(self, user_verification: UserVerification) -> bool:

        user_id: str = self.repository.verify_user_by_code(user_verification)

        if user_id != "" :
            update_verification_status = self.repository.update_verification_status(user_id)
            return update_verification_status

        return False


    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user and all their associated data
        """
        try:
            user = self.repository.get_user_by_id(user_id)
            if user is None:
                raise Exception("Utilisateur non trouvé")

            success = self.repository.delete_user(user_id)

            if not success:
                raise Exception("La suppression de l'utilisateur a échoué")

            return success

        except Exception as e:
            raise Exception(f"Erreur lors de la suppression: {str(e)}")


    def send_password_reset_email(self, email: str) -> bool:
        """
        Send a password reset email
        :param email: The email of the user
        :return: success of the operation
        """
        user_exists = self.get_user_by_email(email)

        if user_exists is None:
            raise Exception("Utilisateur non trouvé")

        password_reset_token = user_exists.password_reset_token
        url = f"https://app.watchbox-app.fr/resetPassword/{password_reset_token}"

        try:
            html = f"""\
            <b>Bonjour, {user_exists.username}</b><br/>
            Voici le <a href="{url}">lien</a> pour réinitialiser votre mot de passe watchbox
            """
            send_mail(email, "Réinitialisation de votre mot de passe Watchbox", html)

            return True

        except Exception as e:
            print(e)
            return False


    def check_password_reset_token(self, password_reset_token: str) -> str:
        try:
            user_id = self.repository.check_password_reset_token(password_reset_token)
            return user_id
        except Exception as e:
            print(e)
            return ""


    def reset_user_password(self, new_password: UserPassword) -> bool:
        # Hash user password with pepper
        pepper = os.getenv("PEPPER")
        hashed_password = sha256((new_password.password + pepper).encode('utf-8'))
        new_password.password = hashed_password.hexdigest()

        # Generate password reset token
        password_reset_token_uuid = uuid.uuid4()
        hashed_password_reset_token = sha256(str(password_reset_token_uuid).encode('utf-8'))
        password_reset_token = hashed_password_reset_token.hexdigest()
        new_password.token = password_reset_token

        update_result = self.repository.update_user_password(new_password)

        return update_result