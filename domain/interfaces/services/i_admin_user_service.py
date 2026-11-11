from typing import Protocol
from uuid import UUID

from domain.models.admin_user import AdminUserCreate, AdminUserUpdate


class IAdminUserService(Protocol):
    def get_users(self, page: int, limit: int) -> dict:
        ...

    def get_user(self, user_id: UUID) -> dict:
        ...

    def create_user(self, data: AdminUserCreate) -> dict:
        ...

    def update_user(self, user_id: UUID, data: AdminUserUpdate) -> dict:
        ...

    def delete_user(self, user_id: UUID) -> dict:
        ...
