from dataclasses import dataclass


@dataclass()
class UserPassword:
    token: str
    password: str
    salt: str
