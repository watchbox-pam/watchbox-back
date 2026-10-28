import datetime
import os

import jwt
from dotenv import load_dotenv

from domain.models.authErrors import InvalidRegistrationTokenError

load_dotenv()

REGISTRATION_TOKEN_PURPOSE = "external_registration"
REGISTRATION_TOKEN_MINUTES = 15


def create_registration_token(provider: str, provider_user_id: str, email: str) -> str:
    """
    Jeton temporaire remis à l'app quand un compte Google / Apple n'existe pas encore.
    Il prouve, pendant 15 minutes, que le backend a déjà vérifié l'identité de la personne.
    Il ne contient pas de "user_id" : il ne peut donc pas servir de jeton de session.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "purpose": REGISTRATION_TOKEN_PURPOSE,
        "provider": provider,
        "sub": provider_user_id,
        "email": email,
        "iat": now,
        "exp": now + datetime.timedelta(minutes=REGISTRATION_TOKEN_MINUTES),
    }
    return jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM"))


def read_registration_token(token: str) -> dict:
    """
    :return: {"provider", "sub", "email"}
    :raises InvalidRegistrationTokenError: jeton invalide, falsifié ou expiré
    """
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")])
    except jwt.ExpiredSignatureError as error:
        raise InvalidRegistrationTokenError("L'inscription a expiré, veuillez recommencer") from error
    except jwt.PyJWTError as error:
        raise InvalidRegistrationTokenError("Jeton d'inscription invalide") from error

    if payload.get("purpose") != REGISTRATION_TOKEN_PURPOSE or not payload.get("sub") or not payload.get("email"):
        raise InvalidRegistrationTokenError("Jeton d'inscription invalide")

    return {"provider": payload.get("provider"), "sub": payload["sub"], "email": payload["email"]}
