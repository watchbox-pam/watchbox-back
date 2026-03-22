import datetime
from typing import Optional

import db_config
from domain.interfaces.repositories.i_user_repository import IUserRepository
from domain.models.user import User
from domain.models.userSignup import UserSignup
from domain.models.userVerification import UserVerification


class UserRepository(IUserRepository):
    def create_user(self, user: UserSignup, password_reset_token: str, verification_code: str, verification_code_token: str) -> bool:

        success: bool = False

        try:
            with db_config.connect_to_db() as conn:

                with conn.cursor() as cur:

                    query = ("INSERT INTO public.user"
                             "(id, username, email, password, salt, birthdate, country, profile_picture_path, banner_path, is_private, history_private, adult_content, last_connection, created_at, is_verified, password_reset_token, verification_code, verification_code_token) "
                             "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);")

                    values = (user.id, user.username, user.email, user.password, user.salt, user.birthdate, user.country, "default.png", "default.png", False, False, False, datetime.datetime.now(), datetime.datetime.now(), False, password_reset_token, verification_code, verification_code_token)

                    cur.execute(query, values)

                    success = True

        except Exception as e:
            print(e)

        return success


    def get_user_by_username(self, username: str) -> Optional[User]:
        user: Optional[User] = None
        try:
            with db_config.connect_to_db() as conn:

                with conn.cursor() as cur:

                    cur.execute("""SELECT id, username, email, password, birthdate, is_private, 
                                   history_private, adult_content, last_connection, created_at,
                                   salt, country, profile_picture_path, banner_path, is_verified,
                                   password_reset_token, verification_code, verification_code_token FROM public.user WHERE username=%s;""", (username,))

                    result = cur.fetchone()

                    if result is not None:
                        user = User(
                            id=result[0],
                            username=result[1],
                            email=result[2],
                            password=result[3],
                            birthdate=result[4],
                            is_private=result[5],
                            history_private=result[6],
                            adult_content=result[7],
                            last_connection=result[8],
                            created_at=result[9],
                            salt=result[10],
                            country=result[11],
                            profile_picture_path=result[12],
                            banner_path=result[13],
                            is_verified=result[14],
                            password_reset_token=result[15],
                            verification_code=result[16],
                            verification_code_token=result[17]
                        )

        except Exception as e:
            print(e)

        return user


    def get_user_by_email(self, email: str) -> Optional[User]:
        user: Optional[User] = None
        try:
            with db_config.connect_to_db() as conn:

                with conn.cursor() as cur:

                    cur.execute("""SELECT id, username, email, password, birthdate, is_private, 
                                   history_private, adult_content, last_connection, created_at,
                                   salt, country, profile_picture_path, banner_path, is_verified,
                                   password_reset_token, verification_code, verification_code_token FROM public.user WHERE email=%s;""", (email,))

                    result = cur.fetchone()

                    if result is not None:
                        user = User(
                            id=result[0],
                            username=result[1],
                            email=result[2],
                            password=result[3],
                            birthdate=result[4],
                            is_private=result[5],
                            history_private=result[6],
                            adult_content=result[7],
                            last_connection=result[8],
                            created_at=result[9],
                            salt=result[10],
                            country=result[11],
                            profile_picture_path=result[12],
                            banner_path=result[13],
                            is_verified=result[14],
                            password_reset_token=result[15],
                            verification_code=result[16],
                            verification_code_token=result[17]
                        )

        except Exception as e:
            print(e)

        return user


    def get_user_by_id(self, id: str) -> Optional[User]:
        user: Optional[User] = None
        try:
            with db_config.connect_to_db() as conn:

                with conn.cursor() as cur:

                    cur.execute("""SELECT id, username, email, password, birthdate, is_private, 
                                   history_private, adult_content, last_connection, created_at,
                                   salt, country, profile_picture_path, banner_path, is_verified,
                                   password_reset_token, verification_code, verification_code_token FROM public.user WHERE id=%s;""", (id,))

                    result = cur.fetchone()

                    if result is not None:
                        user = User(
                            id=result[0],
                            username=result[1],
                            email=result[2],
                            password=result[3],
                            birthdate=result[4],
                            is_private=result[5],
                            history_private=result[6],
                            adult_content=result[7],
                            last_connection=result[8],
                            created_at=result[9],
                            salt=result[10],
                            country=result[11],
                            profile_picture_path=result[12],
                            banner_path=result[13],
                            is_verified=result[14],
                            password_reset_token=result[15],
                            verification_code=result[16],
                            verification_code_token=result[17]
                        )

        except Exception as e:
            print(e)

        return user


    def verify_user_by_code(self, user_verification: UserVerification) -> str:
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM public.user WHERE verification_code=%s AND verification_code_token=%s", (user_verification.code, user_verification.token,))

                    result = cur.fetchone()

                    if result is not None:
                        return result[0]
                    else:
                        return ""

        except (Exception) as e:
            print(e)
            return ""


    def update_verification_status(self, id: str) -> bool:
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:

                    query = ("UPDATE public.user SET is_verified=%s WHERE id=%s")

                    values = (True, id)

                    cur.execute(query, values)

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
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    # Delete user (cascade will handle related data if configured)
                    query = "DELETE FROM public.user WHERE id=%s;"
                    cur.execute(query, (user_id,))

                    success = cur.rowcount > 0

        except Exception as e:
            print(f"Error deleting user: {e}")

        return success