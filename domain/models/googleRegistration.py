from dataclasses import dataclass
from datetime import date


@dataclass()
class GoogleRegistration:
    """Données envoyées par l'app pour finaliser une inscription commencée avec Google."""
    registration_token: str
    username: str
    birthdate: date
    country: str
