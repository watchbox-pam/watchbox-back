from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from api.auth.verify_auth_token import check_jwt_token, get_adult_content
from domain.interfaces.services.i_user_provider_service import IUserProviderService
from domain.models.providerErrors import InvalidProviderError, ProviderCatalogUnavailableError
from repository.onboarding_movie_repository import OnboardingMovieRepository
from repository.provider_repository import ProviderRepository
from repository.user_provider_repository import UserProviderRepository
from service.onboarding_movie_service import OnboardingMovieService
from service.user_provider_service import UserProviderService

user_me_router = APIRouter(prefix="/users/me", tags=["Users"])


def get_user_provider_service() -> IUserProviderService:
    return UserProviderService(UserProviderRepository(), ProviderRepository())


def get_onboarding_movie_service() -> OnboardingMovieService:
    return OnboardingMovieService(OnboardingMovieRepository(), UserProviderRepository())


class UpdateUserProvidersRequest(BaseModel):
    provider_ids: List[int] = Field(default_factory=list, max_length=100)


@user_me_router.get("/providers")
async def get_my_providers(
    user_id: str = Depends(check_jwt_token),
    service: IUserProviderService = Depends(get_user_provider_service)
):
    """Plateformes de streaming de l'utilisateur connecté."""
    return service.get_user_providers(user_id)


@user_me_router.put("/providers")
async def update_my_providers(
    request: UpdateUserProvidersRequest,
    user_id: str = Depends(check_jwt_token),
    service: IUserProviderService = Depends(get_user_provider_service)
):
    """Remplace toute la sélection (liste vide = aucune plateforme)."""
    try:
        return service.set_user_providers(user_id, request.provider_ids)
    except InvalidProviderError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except ProviderCatalogUnavailableError:
        raise HTTPException(status_code=503, detail="Liste des plateformes indisponible, réessayez plus tard")


@user_me_router.get("/onboarding")
async def get_my_onboarding(
    user_id: str = Depends(check_jwt_token),
    service: IUserProviderService = Depends(get_user_provider_service)
):
    completed_at = service.get_onboarding_completed_at(user_id)
    return {"onboarding_completed": completed_at is not None, "onboarding_completed_at": completed_at}


@user_me_router.post("/onboarding/complete")
async def complete_my_onboarding(
    user_id: str = Depends(check_jwt_token),
    service: IUserProviderService = Depends(get_user_provider_service)
):
    """Appelé à la fin du swipe d'onboarding, ou quand l'utilisateur le passe."""
    completed_at = service.complete_onboarding(user_id)
    return {"onboarding_completed": completed_at is not None, "onboarding_completed_at": completed_at}


@user_me_router.get("/onboarding/movies")
async def get_my_onboarding_movies(
    count: int = Query(default=15, ge=1, le=30),
    user_id: str = Depends(check_jwt_token),
    include_adult: bool = Depends(get_adult_content),
    service: OnboardingMovieService = Depends(get_onboarding_movie_service)
):
    """
    Films à swiper pendant l'onboarding : populaires, variés en genres,
    en priorité disponibles sur les plateformes de l'utilisateur. Liste vide possible.
    """
    return service.get_onboarding_movies(user_id, count, include_adult)
