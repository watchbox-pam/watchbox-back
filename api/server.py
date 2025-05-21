import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.applications import AppType
from fastapi.middleware.cors import CORSMiddleware

from api.SearchRouter import search_router
from api.auth.verify_auth_token import check_jwt_token
from api.countryRouter import country_router
from api.movieRouter import movie_router
from api.providerRouter import provider_router
from api.recommendationRouter import recommendation_router
from api.userRouter import user_router
from api.playlistRouter import playlist_router
from api.personRouter import person_router
from api.reviewRouter import review_router


load_dotenv()

origins: list[str] = [
    os.getenv("FRONTEND_BASE_URL")
]

def initServer(app: FastAPI) -> AppType:

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    app.include_router(country_router)
    app.include_router(movie_router, dependencies=[Depends(check_jwt_token)])
    app.include_router(recommendation_router, dependencies=[Depends(check_jwt_token)])
    app.include_router(user_router)
    app.include_router(playlist_router, dependencies=[Depends(check_jwt_token)])
    app.include_router(person_router)
    app.include_router(review_router, dependencies=[Depends(check_jwt_token)])
    app.include_router(search_router)
    app.include_router(provider_router, dependencies=[Depends(check_jwt_token)])

    return app