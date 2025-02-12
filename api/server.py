from fastapi import FastAPI
from fastapi.applications import AppType


def initServer(app: FastAPI) -> AppType:
    #app.include_router()
    return app