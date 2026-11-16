import traceback

from fastapi import APIRouter, Depends, HTTPException, Query

from api.admin.dependencies import to_http_exception
from domain.interfaces.repositories.i_admin_movie_repository import IAdminMovieRepository
from domain.interfaces.services.i_admin_movie_service import IAdminMovieService
from domain.models.admin_errors import AdminError
from domain.models.admin_movie import AdminMovieCreate, AdminMovieUpdate
from repository.admin_movie_repository import AdminMovieRepository
from service.admin_movie_service import AdminMovieService

router = APIRouter(prefix="/movies")


def get_admin_movie_service() -> IAdminMovieService:
    repository: IAdminMovieRepository = AdminMovieRepository()
    return AdminMovieService(repository)


@router.get("")
def get_admin_movies(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=25, ge=1, le=100),
    service: IAdminMovieService = Depends(get_admin_movie_service)
):
    try:
        return service.get_movies(page, limit)

    except Exception as e:
        print(f"[ADMIN] Erreur récupération films : {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération des films"
        )


@router.get("/{movie_id}")
def get_admin_movie(
    movie_id: int,
    service: IAdminMovieService = Depends(get_admin_movie_service)
):
    try:
        return service.get_movie(movie_id)

    except AdminError as e:
        raise to_http_exception(e)

    except Exception as e:
        print(f"[ADMIN] Erreur récupération film {movie_id} : {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération du film"
        )


@router.put("/{movie_id}")
def update_admin_movie(
    movie_id: int,
    data: AdminMovieUpdate,
    service: IAdminMovieService = Depends(get_admin_movie_service)
):
    try:
        return service.update_movie(movie_id, data)

    except AdminError as e:
        raise to_http_exception(e)

    except Exception as e:
        print(f"[ADMIN] Erreur modification film {movie_id} : {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la modification du film"
        )


@router.post("")
def create_admin_movie(
    data: AdminMovieCreate,
    service: IAdminMovieService = Depends(get_admin_movie_service)
):
    try:
        return service.create_movie(data)

    except AdminError as e:
        raise to_http_exception(e)

    except Exception as e:
        print(f"[ADMIN] Erreur création film {data.id} : {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.delete("/{movie_id}")
def delete_admin_movie(
    movie_id: int,
    service: IAdminMovieService = Depends(get_admin_movie_service)
):
    try:
        return service.delete_movie(movie_id)

    except AdminError as e:
        raise to_http_exception(e)

    except Exception as e:
        print(f"[ADMIN] Erreur suppression film {movie_id} : {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la suppression du film"
        )
