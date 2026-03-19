from typing import Protocol, Optional

from domain.models.userPassword import UserPassword
from domain.models.userSignup import UserSignup
from domain.models.user import User
from domain.models.userVerification import UserVerification


class IUserRepository(Protocol):
    def create_user(self, user: UserSignup, password_reset_token: str, verification_code: str, verification_code_token: str) -> bool:
        ...

    def get_user_by_username(self, username: str) -> Optional[User]:
        ...

    def get_user_by_email(self, email: str) -> Optional[User]:
        ...

    def get_user_by_id(self, id: str) -> Optional[User]:
        ...

    def verify_user_by_code(self, user_verification: UserVerification) -> str:
        ...

    def update_verification_status(self, id: str) -> bool:
        ...

    def delete_user(self, user_id: str) -> bool:
        ...

    def check_password_reset_token(self, password_reset_token: str) -> str:
        ...

    def update_user_password(self, new_password: UserPassword) -> bool:
        ...