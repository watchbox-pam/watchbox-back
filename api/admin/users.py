from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from api.admin.dependencies import to_http_exception
from domain.interfaces.repositories.i_admin_user_repository import IAdminUserRepository
from domain.interfaces.services.i_admin_user_service import IAdminUserService
from domain.models.admin_errors import AdminError
from domain.models.admin_user import AdminUserCreate, AdminUserUpdate
from repository.admin_user_repository import AdminUserRepository
from service.admin_user_service import AdminUserService

router = APIRouter(prefix="/users")


def get_admin_user_service() -> IAdminUserService:
    repository: IAdminUserRepository = AdminUserRepository()
    return AdminUserService(repository)


@router.get("")
def get_admin_users(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=25, ge=1, le=100),
    service: IAdminUserService = Depends(get_admin_user_service)
):
    try:
        return service.get_users(page, limit)

    except Exception as e:
        print(f"[ADMIN] Erreur récupération utilisateurs : {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération des utilisateurs"
        )


@router.get("/{user_id}")
def get_admin_user(
    user_id: UUID,
    service: IAdminUserService = Depends(get_admin_user_service)
):
    try:
        return service.get_user(user_id)

    except AdminError as e:
        raise to_http_exception(e)

    except Exception as e:
        print(f"[ADMIN] Erreur récupération utilisateur {user_id} : {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération de l'utilisateur"
        )


@router.put("/{user_id}")
def update_admin_user(
    user_id: UUID,
    data: AdminUserUpdate,
    service: IAdminUserService = Depends(get_admin_user_service)
):
    try:
        return service.update_user(user_id, data)

    except AdminError as e:
        raise to_http_exception(e)

    except Exception as e:
        print(f"[ADMIN] Erreur modification utilisateur {user_id} : {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la modification de l'utilisateur"
        )


@router.delete("/{user_id}")
def delete_admin_user(
    user_id: UUID,
    service: IAdminUserService = Depends(get_admin_user_service)
):
    try:
        return service.delete_user(user_id)

    except AdminError as e:
        raise to_http_exception(e)

    except Exception as e:
        print(f"[ADMIN] Erreur suppression utilisateur {user_id} : {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la suppression de l'utilisateur"
        )


@router.post("")
def create_admin_user(
    data: AdminUserCreate,
    service: IAdminUserService = Depends(get_admin_user_service)
):
    try:
        return service.create_user(data)

    except AdminError as e:
        raise to_http_exception(e)

    except Exception as e:
        print(f"[ADMIN] Erreur création utilisateur : {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la création de l'utilisateur"
        )
