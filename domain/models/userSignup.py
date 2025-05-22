from dataclasses import dataclass
from datetime import date


@dataclass()
class UserSignup:
    id: str
    username: str
    email: str
    password: str
    salt: str
    country: str
    birthdate: date