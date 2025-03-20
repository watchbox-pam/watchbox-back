from dataclasses import dataclass


@dataclass(frozen=True)
class UserLogin:
    identifier: str
    password: str