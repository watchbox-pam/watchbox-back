from fastapi import FastAPI
from fastapi.applications import AppType

from api.movieRouter import movie_router


def initServer(app: FastAPI) -> AppType:
    app.include_router(movie_router)
    return app