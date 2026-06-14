import os
import threading
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.applications import AppType
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from api.SearchRouter import search_router
from api.quizRouter import quiz_router
from api.auth.verify_auth_token import check_jwt_token
from api.countryRouter import country_router
from api.movieRouter import movie_router
from api.providerRouter import provider_router
from api.recommendationRouter import recommendation_router
from api.userRouter import user_router
from api.playlistRouter import playlist_router
from api.personRouter import person_router
from api.reviewRouter import review_router
from api.swipeRouter import swipe_router
from repository.recommentation_repository import RecommendationRepository
from repository.playlist_repository import PlaylistRepository
from repository.quiz_repository import QuizRepository
from service.training_service import TrainingService
from service.ml_state import refresh_ml
from service.quiz_service import QuizService, GENRE_SLUG_TO_ID

load_dotenv()

origins: list[str] = [os.getenv("FRONTEND_BASE_URL")]
training_service = TrainingService(RecommendationRepository(), PlaylistRepository())
scheduler = BackgroundScheduler()

def _train_and_refresh():
    training_service.build_and_train()
    refresh_ml()

def _prewarm_quiz():
    service = QuizService(QuizRepository())
    for genre_slug in GENRE_SLUG_TO_ID:
        try:
            repo = QuizRepository()
            if repo.count_questions(genre_slug) < 10:
                print(f"Génération quiz : {genre_slug}…")
                service.generate_questions(genre_slug)
                print(f"Quiz {genre_slug} prêt.")
        except Exception as e:
            print(f"Erreur pré-chauffe quiz {genre_slug}: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Entraînement initial du modèle ML...")
    _train_and_refresh()
    print("Modèle prêt !")
    threading.Thread(target=_prewarm_quiz, daemon=True).start()
    scheduler.add_job(_train_and_refresh, 'cron', hour=3)
    scheduler.start()
    print("Scheduler démarré.")
    yield
    scheduler.shutdown()

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
    app.include_router(person_router, dependencies=[Depends(check_jwt_token)])
    app.include_router(review_router, dependencies=[Depends(check_jwt_token)])
    app.include_router(search_router, dependencies=[Depends(check_jwt_token)])
    app.include_router(provider_router, dependencies=[Depends(check_jwt_token)])
    app.include_router(swipe_router, dependencies=[Depends(check_jwt_token)])
    app.include_router(quiz_router, dependencies=[Depends(check_jwt_token)])
    return app