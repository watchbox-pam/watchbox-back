import datetime
from typing import Optional

import db_config
from domain.interfaces.repositories.i_user_repository import IUserRepository
from domain.models.user import User
from domain.models.userSignup import UserSignup


class UserRepository(IUserRepository):
    def create_user(self, user: UserSignup) -> bool:

        success: bool = False

        try:
            with db_config.connect_to_db() as conn:

                with conn.cursor() as cur:

                    query = ("INSERT INTO public.user"
                             "(id, username, email, password, salt, birthdate, country, profile_picture_path, banner_path, is_private, history_private, adult_content, last_connection, created_at) "
                             "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);")

                    values = (user.id, user.username, user.email, user.password, user.salt, user.birthdate, user.country, "default.png", "default.png", False, False, False, datetime.datetime.now(), datetime.datetime.now())

                    cur.execute(query, values)

                    success = True

        except (Exception) as e:
            print(e)

        return success


    def get_user_by_username(self, username: str) -> Optional[User]:
        user: Optional[User] = None
        try:
            with db_config.connect_to_db() as conn:

                with conn.cursor() as cur:

                    cur.execute("SELECT * FROM public.user WHERE username=%s;", (username,))

                    result = cur.fetchone()

                    if result is not None:
                        user = User(
                            id=result[0],
                            username=result[1],
                            email=result[2],
                            password=result[3],
                            birthdate=result[4],
                            country=result[5],
                            profile_picture_path=result[6],
                            banner_path=result[7],
                            is_private=result[8],
                            history_private=result[9],
                            adult_content=result[10],
                            last_connection=result[11],
                            created_at=result[12],
                            salt=result[13],
                        )

        except (Exception) as e:
            print(e)

        return user


    def get_user_by_email(self, email: str) -> Optional[User]:
        user: Optional[User] = None
        try:
            with db_config.connect_to_db() as conn:

                with conn.cursor() as cur:

                    cur.execute("SELECT * FROM public.user WHERE email=%s;", (email,))

                    result = cur.fetchone()

                    if result is not None:
                        user = User(
                            id=result[0],
                            username=result[1],
                            email=result[2],
                            password=result[3],
                            birthdate=result[4],
                            country=result[5],
                            profile_picture_path=result[6],
                            banner_path=result[7],
                            is_private=result[8],
                            history_private=result[9],
                            adult_content=result[10],
                            last_connection=result[11],
                            created_at=result[12],
                            salt=result[13],
                        )

        except (Exception) as e:
            print(e)

        return user


    def get_user_by_id(self, id: str) -> Optional[User]:
        user: Optional[User] = None
        try:
            with db_config.connect_to_db() as conn:

                with conn.cursor() as cur:

                    cur.execute("SELECT * FROM public.user WHERE id=%s;", (id,))

                    result = cur.fetchone()

                    if result is not None:
                        user = User(
                            id=result[0],
                            username=result[1],
                            email=result[2],
                            password=result[3],
                            birthdate=result[4],
                            country=result[5],
                            profile_picture_path=result[6],
                            banner_path=result[7],
                            is_private=result[8],
                            history_private=result[9],
                            adult_content=result[10],
                            last_connection=result[11],
                            created_at=result[12],
                            salt=result[13],
                        )

        except (Exception) as e:
            print(e)

        return user