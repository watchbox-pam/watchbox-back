import os
import random
import re
import unicodedata
import uuid
from dotenv import load_dotenv
from hashlib import sha256
from typing import Callable, Optional

from api.auth.verify_auth_token import create_jwt_token
from domain.interfaces.repositories.i_playlist_repository import IPlaylistRepository
from domain.interfaces.repositories.i_user_repository import IUserRepository
from domain.interfaces.services.i_user_service import IUserService
from domain.models.authErrors import AccountConflictError, InvalidRegistrationTokenError
from domain.models.googleRegistration import GoogleRegistration
from domain.models.user import User
from domain.models.userLogin import UserLogin
from domain.models.userPassword import UserPassword
from domain.models.userSignup import UserSignup
from domain.models.userVerification import UserVerification
from utils.google_auth import is_google_email_verified, verify_google_id_token
from utils.mail_service import send_mail
from utils.registration_token import create_registration_token, read_registration_token

load_dotenv()


class UserService(IUserService):
    def __init__(
        self,
        repository: IUserRepository,
        playlist_repository: IPlaylistRepository,
        google_token_verifier: Callable[[str], dict] = verify_google_id_token
    ):
        self.repository = repository
        self.playlist_repository = playlist_repository
        # Remplaçable dans les tests pour ne pas appeler Google
        self.google_token_verifier = google_token_verifier

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


    def get_user_by_username(self, username: str) -> Optional[User]:
        user = self.repository.get_user_by_username(username)
        return user


    def get_user_by_email(self, email: str) -> Optional[User]:
        user = self.repository.get_user_by_email(email)
        return user


    def login_user(self, user: UserLogin) -> dict:
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

        # Compte créé avec Google / Apple : pas de mot de passe
        if not user_exists.password or not user_exists.salt:
            raise Exception("Ce compte utilise la connexion avec Google. Utilisez le bouton « Continuer avec Google ».")

        salted_password = sha256((user.password + user_exists.salt).encode('utf-8')).hexdigest()

        pepper = os.getenv("PEPPER")
        hashed_password = sha256((salted_password + pepper).encode('utf-8'))

        if hashed_password.hexdigest() == user_exists.password:
            user_token = create_jwt_token({
                "user_id": str(user_exists.id)
            })

            return {
                "user_id": str(user_exists.id),
                "token": user_token,
                "username": user_exists.username
            }
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


    def update_settings(self, user_id: str, adult_content: bool, is_private: bool, history_private: bool) -> bool:
        return self.repository.update_settings(user_id, adult_content, is_private, history_private)

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

    def get_password_reset_token(self, user_id: str) -> str:
        return self.repository.get_password_reset_token(user_id)


    # ---------- Connexion / inscription avec Google ----------

    GOOGLE_PROVIDER = "google"

    def login_with_google(self, id_token: str) -> dict:
        """
        Étape 1 du parcours Google, à partir de l'ID token envoyé par l'app :
        - compte Google déjà rattaché : connexion ;
        - un compte existe déjà avec cette adresse mail : on y rattache le compte Google, puis connexion ;
        - sinon : rien n'est créé, on renvoie un jeton d'inscription temporaire (15 min)
          pour que l'app demande le pseudo, la date de naissance et le pays.
        """
        claims = self.google_token_verifier(id_token)

        google_id = claims.get("sub")
        email = (claims.get("email") or "").strip().lower()

        if not google_id or not email:
            raise Exception("Ce compte Google ne fournit pas d'adresse mail")

        if not is_google_email_verified(claims):
            raise Exception("L'adresse mail de ce compte Google n'est pas vérifiée")

        user = self.repository.get_user_by_provider_identity(self.GOOGLE_PROVIDER, google_id)
        if user is not None:
            self.repository.update_last_connection(str(user.id))
            return self._logged_in_response(user)

        existing_user = self.repository.get_user_by_email_insensitive(email)
        if existing_user is not None:
            return self._link_and_log_in(existing_user, google_id)

        return {
            "status": "registration_required",
            "registration_token": create_registration_token(self.GOOGLE_PROVIDER, google_id, email),
            "email": email,
            "suggested_username": self._suggest_username(claims, email)
        }

    def register_with_google(self, registration: GoogleRegistration) -> dict:
        """
        Étape 2 : l'utilisateur a rempli pseudo, date de naissance et pays.
        Crée le compte (sans mot de passe), le rattache au compte Google, crée ses playlists, puis le connecte.
        """
        data = read_registration_token(registration.registration_token)
        if data["provider"] != self.GOOGLE_PROVIDER:
            raise InvalidRegistrationTokenError("Jeton d'inscription invalide")

        google_id, email = data["sub"], data["email"]

        # Double envoi du formulaire : le compte existe déjà, on connecte simplement
        already_registered = self.repository.get_user_by_provider_identity(self.GOOGLE_PROVIDER, google_id)
        if already_registered is not None:
            return self._logged_in_response(already_registered)

        # Compte classique créé entre-temps avec la même adresse : on le rattache (même règle qu'à l'étape 1)
        existing_user = self.repository.get_user_by_email_insensitive(email)
        if existing_user is not None:
            return self._link_and_log_in(existing_user, google_id)

        username = (registration.username or "").strip()
        if not username:
            raise Exception("Le pseudo est requis")
        if len(username) > 50:
            raise Exception("Le pseudo ne doit pas dépasser 50 caractères")
        if self.get_user_by_username(username) is not None:
            raise AccountConflictError("Ce pseudo est déjà utilisé")

        if not registration.birthdate:
            raise Exception("La date de naissance est requise")

        country = (registration.country or "").strip()
        if not country:
            raise Exception("Le pays est requis")
        if not self.repository.country_exists(country):
            raise Exception("Ce pays n'est pas valide")

        if len(email) > 50:
            raise Exception("Cette adresse mail est trop longue pour créer un compte Watchbox")

        user_id = str(uuid.uuid4())
        created = self.repository.create_external_user(
            user_id=user_id,
            username=username,
            email=email,
            birthdate=registration.birthdate,
            country=country,
            provider=self.GOOGLE_PROVIDER,
            provider_user_id=google_id,
            password_reset_token=sha256(str(uuid.uuid4()).encode('utf-8')).hexdigest()
        )
        if not created:
            raise Exception("La création du compte a échoué")

        self.playlist_repository.create_playlist_on_register(user_id=user_id)

        user = self.repository.get_user_by_id(user_id)
        if user is None:
            raise Exception("La création du compte a échoué")
        return self._logged_in_response(user)

    def _link_and_log_in(self, existing_user, google_id: str) -> dict:
        linked = self.repository.link_identity(
            user_id=str(existing_user.id),
            provider=self.GOOGLE_PROVIDER,
            provider_user_id=google_id,
            secure_unverified_account=not existing_user.is_verified
        )
        if not linked:
            raise Exception("La connexion avec Google a échoué")
        return self._logged_in_response(existing_user)

    @staticmethod
    def _logged_in_response(user) -> dict:
        """Même contenu que /users/login, avec un statut en plus."""
        return {
            "status": "logged_in",
            "user_id": str(user.id),
            "token": create_jwt_token({"user_id": str(user.id)}),
            "username": user.username
        }

    def _suggest_username(self, claims: dict, email: str) -> str:
        """Pseudo proposé à partir du prénom Google (l'utilisateur peut le modifier)."""
        raw_name = claims.get("given_name") or claims.get("name") or email.split("@")[0]

        # Retire les accents puis garde uniquement les caractères sûrs
        ascii_name = unicodedata.normalize("NFKD", raw_name).encode("ascii", "ignore").decode("ascii")
        base = re.sub(r"[^A-Za-z0-9_.-]", "", ascii_name)[:20]
        if len(base) < 3:
            base = "user"

        if self.get_user_by_username(base) is None:
            return base

        for _ in range(10):
            candidate = f"{base}{random.randint(1000, 9999)}"
            if self.get_user_by_username(candidate) is None:
                return candidate

        return f"{base}{uuid.uuid4().hex[:6]}"
