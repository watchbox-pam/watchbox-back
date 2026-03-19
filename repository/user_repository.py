import datetime
from typing import Optional

import db_config
from database.db import SessionLocal
from database.models import User
from domain.interfaces.repositories.i_user_repository import IUserRepository
from domain.models.userSignup import UserSignup
from domain.models.userVerification import UserVerification

class UserRepository(IUserRepository):
    def create_user(self, user: UserSignup, password_reset_token: str, verification_code: str, verification_code_token: str) -> bool:

        success: bool = False

        try:
            with SessionLocal() as session:
                new_user = User(
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


    def get_user_by_username(self, username: str) -> Optional[User]:
        user: Optional[User] = None
        try:
            with SessionLocal() as session:
                result = session.query(User).filter(User.username == username).first()

                if result is not None:
                    user = User(
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


    def get_user_by_email(self, email: str) -> Optional[User]:
        user: Optional[User] = None
        try:
            with SessionLocal() as session:
                result = session.query(User).filter(User.email == email).first()

                if result is not None:
                    user = User(
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


    def get_user_by_id(self, id: str) -> Optional[User]:
        user: Optional[User] = None
        try:
            with SessionLocal() as session:
                result = session.query(User).filter(User.id == id).first()

                if result is not None:
                    user = User(
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
                result = session.query(User).filter(User.verification_code == user_verification.code, User.verification_code_token == user_verification.token).first()
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
                user = session.query(User).filter(User.id == id).first()
                if user is not None:
                    user.is_verified = True
                    session.commit()
                    return True
                else:
                    return False

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
                user = session.query(User).filter(User.id == user_id).first()
                if user is not None:
                    session.delete(user)
                    session.commit()
                    success = True
                else:
                    success = False

        except Exception as e:
            print(f"Error deleting user: {e}")

        return success