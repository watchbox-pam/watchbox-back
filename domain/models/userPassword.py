from dataclasses import dataclass


@dataclass()
class UserPassword:
    user_id: str
    token: str
    password: str
    salt: str
