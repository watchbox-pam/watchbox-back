import datetime
from typing import Optional, List

from database.db import SessionLocal
from database.models import User as DBUser
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

    def get_all_users(self) -> List[DBUser]:
        try:
            with SessionLocal() as session:
                result = session.query(DBUser).all()
                users = []
                for user in result:
                    users.append(DBUser(
                        id=user.id,
                        username=user.username,
                        email=user.email,
                        birthdate=user.birthdate,
                        is_private=user.is_private,
                        history_private=user.history_private,
                        adult_content=user.adult_content,
                        last_connection=user.last_connection,
                        created_at=user.created_at,
                        country=user.country,
                        is_verified=user.is_verified,
                        country_=user.country_,
                    ))
                return users

        except Exception as e:
            print(e)
            return []



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