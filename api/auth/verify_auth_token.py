from typing import Optional

import jwt
import os

from database.db import SessionLocal
from database.modelsTemp import User as DBUser
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


def get_adult_content(user_id: str = Depends(check_jwt_token)) -> bool:
    user = get_user_by_id(user_id)
    return user.adult_content if user else False


def get_user_by_id(id: str) -> Optional[User]:
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
