import os
import secrets

from fastapi import Header, HTTPException

from domain.models.admin_errors import (
    AdminConfigurationError,
    AdminConflictError,
    AdminError,
    AdminNotFoundError,
    AdminValidationError,
)


def verify_admin_api_key(
    x_admin_api_key: str | None = Header(default=None, alias="X-Admin-API-Key")
):
    expected_key = os.getenv("WATCHBOX_ADMIN_API_KEY")

    if not expected_key:
        raise HTTPException(
            status_code=500,
            detail="Configuration admin manquante"
        )

    if not x_admin_api_key or not secrets.compare_digest(
        x_admin_api_key, expected_key
    ):
        raise HTTPException(
            status_code=401,
            detail="Non autorisé"
        )


_STATUS_BY_ERROR = {
    AdminNotFoundError: 404,
    AdminConflictError: 409,
    AdminValidationError: 400,
    AdminConfigurationError: 500,
}


def to_http_exception(error: AdminError) -> HTTPException:
    """Traduit une erreur métier admin en réponse HTTP."""
    status_code = next(
        (
            code
            for error_type, code in _STATUS_BY_ERROR.items()
            if isinstance(error, error_type)
        ),
        500,
    )

    return HTTPException(status_code=status_code, detail=str(error))
