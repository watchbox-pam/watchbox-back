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

    def update_settings(self, user_id: str, adult_content: bool, is_private: bool, history_private: bool) -> bool:
        ...

    def get_password_reset_token(self, user_id: str) -> str:
        ...

    def get_user_by_provider_identity(self, provider: str, provider_user_id: str) -> Optional[User]:
        ...

    def get_user_by_email_insensitive(self, email: str) -> Optional[User]:
        ...

    def country_exists(self, iso: str) -> bool:
        ...

    def create_external_user(self, user_id: str, username: str, email: str, birthdate, country: str,
                             provider: str, provider_user_id: str, password_reset_token: str) -> bool:
        ...

    def link_identity(self, user_id: str, provider: str, provider_user_id: str, secure_unverified_account: bool) -> bool:
        ...

    def update_last_connection(self, user_id: str) -> None:
        ...
