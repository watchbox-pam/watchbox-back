from typing import Protocol, Optional

from domain.models.user import User
from domain.models.userLogin import UserLogin
from domain.models.userPassword import UserPassword
from domain.models.userSignup import UserSignup
from domain.models.userVerification import UserVerification


class IUserService(Protocol):
    def create_user(self, user: UserSignup) -> dict[str, str]:
        ...

    def get_user_by_username(self, username: str) -> Optional[User]:
        ...

    def get_user_by_email(self, email: str) -> Optional[User]:
        ...

    def login_user(self, user: UserLogin) -> dict[str, str]:
        ...

    def get_user_by_id(self, id: str) -> Optional[User]:
        ...

    def verify_user(self, user: UserVerification) -> bool:
        ...

    def delete_user(self, user_id: str) -> bool:
        ...

    def send_password_reset_email(self, email: str) -> bool:
        ...

    def check_password_reset_token(self, password_reset_token: str) -> str:
        ...

    def reset_user_password(self, new_password: UserPassword) -> bool:
        ...

    def update_settings(self, user_id: str, adult_content: bool, is_private: bool, history_private: bool) -> bool:
        ...