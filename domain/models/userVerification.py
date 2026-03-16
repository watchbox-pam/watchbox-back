from dataclasses import dataclass


@dataclass(frozen=True)
class UserVerification:
    code: str
    token: str