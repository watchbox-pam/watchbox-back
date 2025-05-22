from fastapi import APIRouter, Depends, Query
from fastapi.params import Depends
from starlette.exceptions import HTTPException
from typing import List, Optional

from domain.interfaces.services.i_search_service import ISearchService
from service.search_service import SearchService
from repository.search_repository import SearchRepository

search_router = APIRouter(prefix="/search", tags=["Search"])

def get_search_service() -> ISearchService:
    repository = SearchRepository()
    return SearchService(repository)

@search_router.get("/{search_term}")
async def search_all(
    search_term: str,
    providers: Optional[List[int]] = Query(None),
    service: ISearchService = Depends(get_search_service)
):
    """
    Search all media types (movies, tv, people) based on the given search term
    with optional provider filtering
    """
    try:
        results = service.search_all(search_term, providers)
        return results
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))

@search_router.get("/movie/{search_term}")
async def search_movies(
    search_term: str,
    providers: Optional[List[int]] = Query(None),
    service: ISearchService = Depends(get_search_service)
):
    """
    Search only movies based on the given search term
    with optional provider filtering
    """
    try:
        results = service.search_movies(search_term, providers)
        return results
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))

@search_router.get("/person/{search_term}")
async def search_actors(search_term: str, service: ISearchService = Depends(get_search_service)):
    """
    Search only actors/people based on the given search term
    """
    try:
        results = service.search_actors(search_term)
        return results
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))