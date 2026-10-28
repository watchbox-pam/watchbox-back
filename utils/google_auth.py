import os

import requests
from dotenv import load_dotenv
from google.auth import exceptions as google_exceptions
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from domain.models.authErrors import ExternalAuthUnavailableError, InvalidExternalTokenError

load_dotenv()

GOOGLE_ISSUERS = ("accounts.google.com", "https://accounts.google.com")

# Délai max (secondes) pour télécharger les certificats publics de Google
GOOGLE_CERTS_TIMEOUT = 5

# Session HTTP réutilisée pour télécharger les certificats publics de Google
_http_session = requests.Session()


class _RequestWithTimeout(google_requests.Request):
    """google-auth attend 120 s par défaut : on coupe bien avant pour ne pas bloquer l'API."""

    def __call__(self, url, method="GET", body=None, headers=None, timeout=None, **kwargs):
        return super().__call__(url, method=method, body=body, headers=headers, timeout=timeout or GOOGLE_CERTS_TIMEOUT, **kwargs)


def _allowed_client_ids() -> list[str]:
    """
    GOOGLE_CLIENT_IDS : Client ID OAuth acceptés, séparés par des virgules.
    Avec Google Sign-In configuré avec le Client ID "Web", l'audience (aud)
    du jeton est ce Client ID, sur Android comme sur iOS.
    """
    raw = os.getenv("GOOGLE_CLIENT_IDS", "")
    return [client_id.strip() for client_id in raw.split(",") if client_id.strip()]


def verify_google_id_token(token: str) -> dict:
    """
    Vérifie la signature, l'expiration, l'émetteur et l'audience d'un ID token Google.
    :return: les informations du compte (sub, email, email_verified, given_name...)
    :raises InvalidExternalTokenError: jeton invalide
    :raises ExternalAuthUnavailableError: configuration manquante ou Google injoignable
    """
    client_ids = _allowed_client_ids()
    if not client_ids:
        raise ExternalAuthUnavailableError("Configuration GOOGLE_CLIENT_IDS manquante")

    try:
        # audience=None : on vérifie l'audience nous-mêmes pour accepter plusieurs Client ID
        claims: dict = google_id_token.verify_oauth2_token(
            token,
            _RequestWithTimeout(session=_http_session),
            audience=None,
        )
    except google_exceptions.TransportError as error:
        raise ExternalAuthUnavailableError(f"Certificats Google injoignables : {error}") from error
    except (ValueError, google_exceptions.GoogleAuthError) as error:
        # Signature, expiration, format ou émetteur invalide
        raise InvalidExternalTokenError(f"Jeton Google invalide : {error}") from error

    if claims.get("iss") not in GOOGLE_ISSUERS:
        raise InvalidExternalTokenError("Émetteur du jeton Google invalide")

    if claims.get("aud") not in client_ids:
        raise InvalidExternalTokenError("Ce jeton Google n'a pas été émis pour Watchbox")

    return claims


def is_google_email_verified(claims: dict) -> bool:
    value = claims.get("email_verified")
    return value is True or value == "true"
