from typing import Optional

import jwt
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

import db_config
from domain.models.user import User

load_dotenv()
jwt_secret_key = os.getenv("JWT_SECRET_KEY")
jwt_algorithm = os.getenv("JWT_ALGORITHM")

def create_jwt_token(payload: dict) -> str:
    to_encode = payload.copy()
    encoded_jwt = jwt.encode(to_encode, jwt_secret_key, algorithm=jwt_algorithm)
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def check_jwt_token(token: str = Depends(oauth2_scheme)) -> str:
    try:
        decoded_token = token.strip('\"')
        payload = jwt.decode(decoded_token, jwt_secret_key, algorithms=[jwt_algorithm])
        # Check if user exists in base
        user_exists = get_user_by_id(payload["user_id"])
        if user_exists is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")
        return user_exists.id
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")


def get_user_by_id(id: str) -> Optional[User]:
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

    except (Exception) as e:
        print(e)

    return user
