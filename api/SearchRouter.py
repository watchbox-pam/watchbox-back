from fastapi import APIRouter, Depends, Query
from starlette.exceptions import HTTPException
from typing import List, Optional

from api.auth.verify_auth_token import get_adult_content
from domain.interfaces.services.i_search_service import ISearchService
from service.search_service import SearchService
from repository.search_repository import SearchRepository

search_router = APIRouter(prefix="/search", tags=["Search"])

def get_search_service() -> ISearchService:
    repository = SearchRepository()
    return SearchService(repository)

@search_router.get("/suggestions")
def get_suggestions(
    query: str,
    providers: Optional[List[int]] = Query(default=None),
    include_adult: bool = Depends(get_adult_content),
    service: ISearchService = Depends(get_search_service)
):
    results = service.get_suggestions(query, providers, include_adult)
    return results

@search_router.get("/movie/{search_term}")
async def search_movies(
    search_term: str,
    providers: Optional[List[int]] = Query(None),
    include_adult: bool = Depends(get_adult_content),
    service: ISearchService = Depends(get_search_service)
):
    try:
        results = service.search_movies(search_term, providers, include_adult)
        return results
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))

@search_router.get("/person/{search_term}")
async def search_actors(
    search_term: str,
    include_adult: bool = Depends(get_adult_content),
    service: ISearchService = Depends(get_search_service)
):
    try:
        results = service.search_actors(search_term, include_adult)
        return results
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))

@search_router.get("/users/{search_term}")
async def search_users(
    search_term: str,
    service: ISearchService = Depends(get_search_service)
):
    try:
        results = service.search_users(search_term)
        return results
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))

@search_router.get("/{search_term}")
async def search_all(
    search_term: str,
    providers: Optional[List[int]] = Query(None),
    include_adult: bool = Depends(get_adult_content),
    service: ISearchService = Depends(get_search_service)
):
    try:
        results = service.search_all(search_term, providers, include_adult)
        return results
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
