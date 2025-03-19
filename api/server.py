import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.applications import AppType
from fastapi.middleware.cors import CORSMiddleware

from api.countryRouter import country_router
from api.movieRouter import movie_router
from api.userRouter import user_router


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
    app.include_router(movie_router)
    app.include_router(user_router)
    return app