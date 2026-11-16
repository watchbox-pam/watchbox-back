from typing import Optional, Protocol
from uuid import UUID

from database.models import User as DBUser


class IAdminUserRepository(Protocol):
    def count(self) -> int:
        ...

    def find_page(self, offset: int, limit: int) -> list[DBUser]:
        ...

    def find_by_id(self, user_id: UUID) -> Optional[DBUser]:
        ...

    def username_exists(self, username: str) -> bool:
        ...

    def email_exists(self, email: str) -> bool:
        ...

    def create_with_playlist(self, data: dict) -> DBUser:
        ...

    def update(self, user_id: UUID, data: dict) -> Optional[DBUser]:
        ...

    def delete(self, user_id: UUID) -> bool:
        ...
