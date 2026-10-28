import datetime
from typing import Optional

from sqlalchemy import false, func

from database.db import SessionLocal
from database.models import Country as DBCountry
from database.models import User as DBUser
from database.models import UserIdentity as DBUserIdentity
from domain.interfaces.repositories.i_user_repository import IUserRepository
from domain.models.user import User
from domain.models.userPassword import UserPassword
from domain.models.userSignup import UserSignup
from domain.models.userVerification import UserVerification

class UserRepository(IUserRepository):
    def create_user(self, user: UserSignup, password_reset_token: str, verification_code: str, verification_code_token: str) -> bool:

        success: bool = False

        try:
            with SessionLocal() as session:
                new_user = DBUser(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    password=user.password,
                    salt=user.salt,
                    birthdate=user.birthdate,
                    country=user.country,
                    profile_picture_path="default.png",
                    banner_path="default.png",
                    is_private=False,
                    history_private=False,
                    adult_content=False,
                    last_connection=datetime.datetime.now(),
                    created_at=datetime.datetime.now(),
                    is_verified=False,
                    password_reset_token=password_reset_token,
                    verification_code=verification_code,
                    verification_code_token=verification_code_token,
                    country_=None,
                    playlist=[]
                )
                session.add(new_user)
                session.commit()
                success = True

        except Exception as e:
            print(e)

        return success


    def get_user_by_username(self, username: str) -> Optional[DBUser]:
        user: Optional[DBUser] = None
        try:
            with SessionLocal() as session:
                result = session.query(DBUser).filter(DBUser.username == username).first()

                if result is not None:
                    user = DBUser(
                        id=result.id,
                        username=result.username,
                        email=result.email,
                        password=result.password,
                        birthdate=result.birthdate,
                        is_private=result.is_private,
                        history_private=result.history_private,
                        adult_content=result.adult_content,
                        last_connection=result.last_connection,
                        created_at=result.created_at,
                        salt=result.salt,
                        country=result.country,
                        profile_picture_path=result.profile_picture_path,
                        banner_path=result.banner_path,
                        is_verified=result.is_verified,
                        password_reset_token=result.password_reset_token,
                        verification_code=result.verification_code,
                        verification_code_token=result.verification_code_token,
                        country_=result.country_,
                        playlist=result.playlist
                    )
        except Exception as e:
            print(e)

        return user


    def get_user_by_email(self, email: str) -> Optional[DBUser]:
        user: Optional[DBUser] = None
        try:
            with SessionLocal() as session:
                result = session.query(DBUser).filter(DBUser.email == email).first()

                if result is not None:
                    user = DBUser(
                        id=result.id,
                        username=result.username,
                        email=result.email,
                        password=result.password,
                        birthdate=result.birthdate,
                        is_private=result.is_private,
                        history_private=result.history_private,
                        adult_content=result.adult_content,
                        last_connection=result.last_connection,
                        created_at=result.created_at,
                        salt=result.salt,
                        country=result.country,
                        profile_picture_path=result.profile_picture_path,
                        banner_path=result.banner_path,
                        is_verified=result.is_verified,
                        password_reset_token=result.password_reset_token,
                        verification_code=result.verification_code,
                        verification_code_token=result.verification_code_token,
                        country_=result.country_,
                        playlist=result.playlist
                    )

        except Exception as e:
            print(e)

        return user


    def get_user_by_id(self, id: str) -> Optional[DBUser]:
        user: Optional[DBUser] = None
        try:
            with SessionLocal() as session:
                result = session.query(DBUser).filter(DBUser.id == id).first()

                if result is not None:
                    user = DBUser(
                        id=result.id,
                        username=result.username,
                        email=result.email,
                        password=result.password,
                        birthdate=result.birthdate,
                        is_private=result.is_private,
                        history_private=result.history_private,
                        adult_content=result.adult_content,
                        last_connection=result.last_connection,
                        created_at=result.created_at,
                        salt=result.salt,
                        country=result.country,
                        profile_picture_path=result.profile_picture_path,
                        banner_path=result.banner_path,
                        is_verified=result.is_verified,
                        password_reset_token=result.password_reset_token,
                        verification_code=result.verification_code,
                        verification_code_token=result.verification_code_token,
                        country_=result.country_,
                        playlist=result.playlist
                    )

        except Exception as e:
            print(e)

        return user




    def verify_user_by_code(self, user_verification: UserVerification) -> str:
        try:
            with SessionLocal() as session:
                result = session.query(DBUser).filter(DBUser.verification_code == user_verification.code, DBUser.verification_code_token == user_verification.token).first()
                if result is not None:
                    return result.id
                else:
                    return ""

        except (Exception) as e:
            print(e)
            return ""


    def update_verification_status(self, id: str) -> bool:
        try:
            with SessionLocal() as session:
                user = session.query(DBUser).filter(DBUser.id == id).first()
                if user is not None:
                    user.is_verified = True
                    session.commit()
                    return True
                else:
                    return False

        except Exception as e:
            print(e)
            return False

    def update_settings(self, user_id: str, adult_content: bool, is_private: bool, history_private: bool) -> bool:
        try:
            with SessionLocal() as session:
                user = session.query(DBUser).filter(DBUser.id == user_id).first()
                if user is None:
                    return False
                user.adult_content = adult_content
                user.is_private = is_private
                user.history_private = history_private
                session.commit()
                return True
        except Exception as e:
            print(e)
            return False

    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user and all associated data from the database
        """
        success: bool = False

        try:
            with SessionLocal() as session:
                user = session.query(DBUser).filter(DBUser.id == user_id).first()
                if user is not None:
                    session.delete(user)
                    session.commit()
                    success = True
                else:
                    success = False

        except Exception as e:
            print(f"Error deleting user: {e}")

        return success


    def check_password_reset_token(self, password_reset_token: str) -> str:
        user_id: Optional[str] = None
        try:
            with SessionLocal() as session:
                user = session.query(DBUser).filter(DBUser.password_reset_token == password_reset_token).first()
                if user is not None:
                    user_id = user.id

        except Exception as e:
            print(e)

        return user_id

    def update_user_password(self, new_password: UserPassword) -> bool:
        try:
            with SessionLocal() as session:
                user = session.query(DBUser).filter(DBUser.id == new_password.user_id).first()
                if user is not None:
                    user.password = new_password.password
                    user.salt = new_password.salt
                    user.password_reset_token = new_password.token
                    session.commit()
                    return True
                else:
                    return False

        except Exception as e:
            print(e)
            return False


    def get_password_reset_token(self, user_id: str) -> str:
        try:
            password_reset_token: str = ""
            with SessionLocal() as session:
                user = session.query(DBUser).filter(DBUser.id == user_id).first()
                if user is not None:
                    password_reset_token = user.password_reset_token
            return password_reset_token
        except Exception as e:
            print(e)
            return ""


    # ---------- Connexion via un fournisseur externe (Google, Apple) ----------

    def get_user_by_provider_identity(self, provider: str, provider_user_id: str) -> Optional[DBUser]:
        """Utilisateur rattaché à ce compte Google / Apple, ou None."""
        try:
            with SessionLocal() as session:
                return (
                    session.query(DBUser)
                    .join(DBUserIdentity, DBUserIdentity.user_id == DBUser.id)
                    .filter(
                        DBUserIdentity.provider == provider,
                        DBUserIdentity.provider_user_id == provider_user_id
                    )
                    .first()
                )
        except Exception as e:
            print(e)
            return None

    def get_user_by_email_insensitive(self, email: str) -> Optional[DBUser]:
        """Recherche par email sans tenir compte des majuscules (Google renvoie l'email en minuscules)."""
        try:
            with SessionLocal() as session:
                return (
                    session.query(DBUser)
                    .filter(func.lower(DBUser.email) == email.lower())
                    .first()
                )
        except Exception as e:
            print(e)
            return None

    def country_exists(self, iso: str) -> bool:
        try:
            with SessionLocal() as session:
                return session.query(DBCountry.iso).filter(DBCountry.iso == iso).first() is not None
        except Exception as e:
            print(e)
            return False

    def create_external_user(self, user_id: str, username: str, email: str, birthdate, country: str,
                             provider: str, provider_user_id: str, password_reset_token: str) -> bool:
        """Crée l'utilisateur (sans mot de passe) et le rattache à son compte Google / Apple, dans la même transaction."""
        try:
            with SessionLocal() as session:
                now = datetime.datetime.now()
                # Il faut renseigner la relation country_ avec le vrai pays :
                # si on passe country_=None, SQLAlchemy vide aussi la colonne country à l'enregistrement
                country_row = session.get(DBCountry, country)
                new_user = DBUser(
                    id=user_id,
                    username=username,
                    email=email,
                    password=None,
                    salt=None,
                    birthdate=birthdate,
                    country=country,
                    profile_picture_path="default.png",
                    banner_path="default.png",
                    is_private=False,
                    history_private=False,
                    adult_content=False,
                    last_connection=now,
                    created_at=now,
                    is_verified=True,  # adresse mail déjà vérifiée par Google / Apple
                    password_reset_token=password_reset_token,
                    verification_code=None,
                    verification_code_token=None,
                    country_=country_row,
                    playlist=[]
                )
                session.add(new_user)
                session.flush()

                session.add(DBUserIdentity(
                    user_id=new_user.id,
                    provider=provider,
                    provider_user_id=provider_user_id
                ))
                session.commit()
                return True
        except Exception as e:
            print(e)
            return False

    def link_identity(self, user_id: str, provider: str, provider_user_id: str, secure_unverified_account: bool) -> bool:
        """
        Rattache un compte Google / Apple à un utilisateur existant (même adresse mail).
        secure_unverified_account : l'utilisateur existant n'avait jamais validé son adresse mail.
        Google / Apple prouvent que la personne possède cette adresse : on valide le compte
        et on supprime l'ancien mot de passe, qui a pu être choisi par quelqu'un d'autre.
        """
        try:
            with SessionLocal() as session:
                user = session.query(DBUser).filter(DBUser.id == user_id).first()
                if user is None:
                    return False

                session.add(DBUserIdentity(
                    user_id=user.id,
                    provider=provider,
                    provider_user_id=provider_user_id
                ))

                if secure_unverified_account:
                    user.is_verified = True
                    user.password = None
                    user.salt = None
                    user.verification_code = None
                    user.verification_code_token = None

                user.last_connection = datetime.datetime.now()
                session.commit()
                return True
        except Exception as e:
            print(e)
            return False

    def update_last_connection(self, user_id: str) -> None:
        try:
            with SessionLocal() as session:
                user = session.query(DBUser).filter(DBUser.id == user_id).first()
                if user is not None:
                    user.last_connection = datetime.datetime.now()
                    session.commit()
        except Exception as e:
            print(e)
