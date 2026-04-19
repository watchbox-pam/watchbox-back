import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from service.ml_service import MLService

_ml_instance: "MLService | None" = None


def get_ml() -> "MLService | None":
    return _ml_instance


def refresh_ml() -> None:
    global _ml_instance
    if not os.path.exists("ml_model.pkl"):
        return
    try:
        from service.ml_service import MLService
        _ml_instance = MLService.load("ml_model.pkl")
        print("ML singleton rechargé.")
    except Exception as e:
        print(f"Erreur rechargement ML singleton: {e}")
