import os
import secrets
import traceback
import uuid
import datetime

from hashlib import sha256

from sqlalchemy import func
from uuid import UUID
from datetime import date
from typing import Optional

from pydantic import BaseModel
from fastapi import APIRouter, Depends, Header, HTTPException, Query

from database.db import SessionLocal
from database.models import (
    Movie as DBMovie,
    User as DBUser,
    Playlist as DBPlaylist
)

admin_router = APIRouter(prefix="/admin", tags=["Admin"])

class AdminMovieUpdate(BaseModel):
    adult: Optional[bool] = None
    backdrop_path: Optional[str] = None
    budget: Optional[int] = None
    homepage: Optional[str] = None
    imdb_id: Optional[str] = None
    original_language: Optional[str] = None
    original_title: Optional[str] = None
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    release_date: Optional[date] = None
    revenue: Optional[int] = None
    runtime: Optional[int] = None
    status: Optional[str] = None
    tagline: Optional[str] = None
    title: Optional[str] = None
    video: Optional[str] = None
    infos_complete: Optional[bool] = None

class AdminMovieCreate(BaseModel):
    id: int
    adult: Optional[bool] = None
    backdrop_path: Optional[str] = None
    budget: Optional[int] = None
    homepage: Optional[str] = None
    imdb_id: Optional[str] = None
    original_language: Optional[str] = None
    original_title: Optional[str] = None
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    release_date: Optional[date] = None
    revenue: Optional[int] = None
    runtime: Optional[int] = None
    status: Optional[str] = None
    tagline: Optional[str] = None
    title: Optional[str] = None
    popularity: Optional[float] = None
    video: Optional[str] = None
    infos_complete: Optional[bool] = False

class AdminUserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    country: Optional[str] = None
    birthdate: Optional[date] = None
    profile_picture_path: Optional[str] = None
    banner_path: Optional[str] = None

    is_private: Optional[bool] = None
    history_private: Optional[bool] = None
    adult_content: Optional[bool] = None
    is_verified: Optional[bool] = None

class AdminUserCreate(BaseModel):
    username: str
    email: str
    password: str
    salt: str

    country: Optional[str] = None
    birthdate: date

    profile_picture_path: Optional[str] = None
    banner_path: Optional[str] = None

    is_private: bool = False
    history_private: bool = False
    adult_content: bool = False
    is_verified: bool = True
    is_admin: bool = False

def verify_admin_api_key(
    x_admin_api_key: str | None = Header(default=None, alias="X-Admin-API-Key")
):
    expected_key = os.getenv("WATCHBOX_ADMIN_API_KEY")

    if not expected_key:
        raise HTTPException(
            status_code=500,
            detail="Configuration admin manquante"
        )

    if not x_admin_api_key or not secrets.compare_digest(
        x_admin_api_key, expected_key
    ):
        raise HTTPException(
            status_code=401,
            detail="Non autorisé"
        )


@admin_router.get(
    "/movies",
    dependencies=[Depends(verify_admin_api_key)]
)
def get_admin_movies(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=25, ge=1, le=100)
):
    offset = (page - 1) * limit

    try:
        with SessionLocal() as session:
            total = session.query(func.count(DBMovie.id)).scalar() or 0

            movies = (
                session.query(DBMovie)
                .order_by(DBMovie.title.asc().nullslast())
                .offset(offset)
                .limit(limit)
                .all()
            )

            items = [
                {
                    "id": movie.id,
                    "title": movie.title,
                    "poster_path": movie.poster_path,
                    "release_date": (
                        movie.release_date.isoformat()
                        if movie.release_date
                        else None
                    ),
                    "popularity": movie.popularity,
                    "runtime": movie.runtime,
                    "infos_complete": movie.infos_complete,
                    "adult": movie.adult,
                }
                for movie in movies
            ]

            return {
                "items": items,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "total_pages": (total + limit - 1) // limit,
                },
            }

    except Exception as e:
        print(f"[ADMIN] Erreur récupération films : {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération des films"
        )

@admin_router.get(
    "/movies/{movie_id}",
    dependencies=[Depends(verify_admin_api_key)]
)
def get_admin_movie(movie_id: int):
    try:
        with SessionLocal() as session:
            movie = (
                session.query(DBMovie)
                .filter(DBMovie.id == movie_id)
                .first()
            )

            if not movie:
                raise HTTPException(
                    status_code=404,
                    detail="Film introuvable"
                )

            return {
                "id": movie.id,
                "title": movie.title,
                "poster_path": movie.poster_path,
                "release_date": (
                    movie.release_date.isoformat()
                    if movie.release_date
                    else None
                ),
                "popularity": movie.popularity,
                "runtime": movie.runtime,
                "infos_complete": movie.infos_complete,
                "adult": movie.adult,
            }

    except HTTPException:
        raise

    except Exception as e:
        print(
            f"[ADMIN] Erreur récupération film {movie_id} : {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération du film"
        )
@admin_router.put(
    "/movies/{movie_id}",
    dependencies=[Depends(verify_admin_api_key)]
)
def update_admin_movie(
    movie_id: int,
    data: AdminMovieUpdate
):
    try:
        with SessionLocal() as session:
            movie = (
                session.query(DBMovie)
                .filter(DBMovie.id == movie_id)
                .first()
            )

            if not movie:
                raise HTTPException(
                    status_code=404,
                    detail="Film introuvable"
                )

            update_data = data.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(movie, field, value)

            session.commit()
            session.refresh(movie)

            return {
                "id": movie.id,
                "title": movie.title,
                "poster_path": movie.poster_path,
                "release_date": (
                    movie.release_date.isoformat()
                    if movie.release_date
                    else None
                ),
                "popularity": movie.popularity,
                "runtime": movie.runtime,
                "infos_complete": movie.infos_complete,
                "adult": movie.adult,
            }

    except HTTPException:
        raise

    except Exception as e:
        print(
            f"[ADMIN] Erreur modification film {movie_id} : {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la modification du film"
        )
@admin_router.post(
    "/movies",
    dependencies=[Depends(verify_admin_api_key)]
)
def create_admin_movie(
    data: AdminMovieCreate
):
    try:
        with SessionLocal() as session:

            existing_movie = (
                session.query(DBMovie)
                .filter(DBMovie.id == data.id)
                .first()
            )

            if existing_movie:
                raise HTTPException(
                    status_code=409,
                    detail="Un film avec cet ID existe déjà"
                )

            movie = DBMovie(
                id=data.id,
                adult=data.adult,
                backdrop_path=data.backdrop_path,
                budget=data.budget,
                homepage=data.homepage,
                imdb_id=data.imdb_id,
                original_language=data.original_language,
                original_title=data.original_title,
                overview=data.overview,
                poster_path=data.poster_path,
                release_date=data.release_date,
                revenue=data.revenue,
                runtime=data.runtime,
                status=data.status,
                tagline=data.tagline,
                title=data.title,
                popularity=data.popularity,
                video=data.video,
                infos_complete=data.infos_complete,
                genre = []
            )

            session.add(movie)
            session.commit()
            session.refresh(movie)

            return {
                "id": movie.id,
                "title": movie.title,
                "poster_path": movie.poster_path,
                "release_date": (
                    movie.release_date.isoformat()
                    if movie.release_date
                    else None
                ),
                "popularity": movie.popularity,
                "runtime": movie.runtime,
                "infos_complete": movie.infos_complete,
                "adult": movie.adult,
            }

    except HTTPException:
        raise


    except Exception as e:

        print(

            f"[ADMIN] Erreur création film {data.id} : {e}"

        )

        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@admin_router.delete(
    "/movies/{movie_id}",
    dependencies=[Depends(verify_admin_api_key)]
)
def delete_admin_movie(movie_id: int):
    try:
        with SessionLocal() as session:

            movie = (
                session.query(DBMovie)
                .filter(DBMovie.id == movie_id)
                .first()
            )

            if not movie:
                raise HTTPException(
                    status_code=404,
                    detail="Film introuvable"
                )

            session.delete(movie)
            session.commit()

            return {
                "success": True,
                "id": movie_id
            }

    except HTTPException:
        raise

    except Exception as e:
        print(
            f"[ADMIN] Erreur suppression film {movie_id} : {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la suppression du film"
        )
@admin_router.get(
    "/users",
    dependencies=[Depends(verify_admin_api_key)]
)
def get_admin_users(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=25, ge=1, le=100)
):
    offset = (page - 1) * limit

    try:
        with SessionLocal() as session:

            total = (
                session.query(func.count(DBUser.id))
                .scalar()
                or 0
            )

            users = (
                session.query(DBUser)
                .order_by(DBUser.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )

            items = [
                {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "country": user.country,
                    "birthdate": (
                        user.birthdate.isoformat()
                        if user.birthdate
                        else None
                    ),
                    "profile_picture_path": user.profile_picture_path,
                    "is_private": user.is_private,
                    "history_private": user.history_private,
                    "adult_content": user.adult_content,
                    "is_verified": user.is_verified,
                    "last_connection": (
                        user.last_connection.isoformat()
                        if user.last_connection
                        else None
                    ),
                    "created_at": (
                        user.created_at.isoformat()
                        if user.created_at
                        else None
                    ),
                    "is_admin": user.is_admin,
                }
                for user in users
            ]

            return {
                "items": items,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "total_pages": (
                        (total + limit - 1) // limit
                    ),
                },
            }

    except Exception as e:
        print(f"[ADMIN] Erreur récupération utilisateurs : {e}")

        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération des utilisateurs"
        )

@admin_router.get(
    "/users/{user_id}",
    dependencies=[Depends(verify_admin_api_key)]
)
def get_admin_user(user_id: UUID):
    try:
        with SessionLocal() as session:

            user = (
                session.query(DBUser)
                .filter(DBUser.id == user_id)
                .first()
            )

            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="Utilisateur introuvable"
                )

            return {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "country": user.country,
                "birthdate": (
                    user.birthdate.isoformat()
                    if user.birthdate
                    else None
                ),
                "profile_picture_path": user.profile_picture_path,
                "banner_path": user.banner_path,
                "is_private": user.is_private,
                "history_private": user.history_private,
                "adult_content": user.adult_content,
                "is_verified": user.is_verified,
                "last_connection": (
                    user.last_connection.isoformat()
                    if user.last_connection
                    else None
                ),
                "created_at": (
                    user.created_at.isoformat()
                    if user.created_at
                    else None
                ),
                "is_admin": user.is_admin,
            }

    except HTTPException:
        raise

    except Exception as e:
        print(
            f"[ADMIN] Erreur récupération utilisateur {user_id} : {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération de l'utilisateur"
        )

@admin_router.put(
    "/users/{user_id}",
    dependencies=[Depends(verify_admin_api_key)]
)
def update_admin_user(
    user_id: UUID,
    data: AdminUserUpdate
):
    try:
        with SessionLocal() as session:

            user = (
                session.query(DBUser)
                .filter(DBUser.id == user_id)
                .first()
            )

            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="Utilisateur introuvable"
                )

            update_data = data.model_dump(
                exclude_unset=True
            )

            for field, value in update_data.items():
                setattr(user, field, value)

            session.commit()
            session.refresh(user)

            return {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "country": user.country,
                "birthdate": (
                    user.birthdate.isoformat()
                    if user.birthdate
                    else None
                ),
                "profile_picture_path": user.profile_picture_path,
                "banner_path": user.banner_path,
                "is_private": user.is_private,
                "history_private": user.history_private,
                "adult_content": user.adult_content,
                "is_verified": user.is_verified,
                "last_connection": (
                    user.last_connection.isoformat()
                    if user.last_connection
                    else None
                ),
                "created_at": (
                    user.created_at.isoformat()
                    if user.created_at
                    else None
                ),
                "is_admin": user.is_admin,
            }

    except HTTPException:
        raise

    except Exception as e:
        print(
            f"[ADMIN] Erreur modification utilisateur {user_id} : {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la modification de l'utilisateur"
        )

@admin_router.delete(
    "/users/{user_id}",
    dependencies=[Depends(verify_admin_api_key)]
)
def delete_admin_user(user_id: UUID):
    try:
        with SessionLocal() as session:

            user = (
                session.query(DBUser)
                .filter(DBUser.id == user_id)
                .first()
            )

            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="Utilisateur introuvable"
                )

            session.delete(user)
            session.commit()

            return {
                "success": True,
                "id": str(user_id)
            }

    except HTTPException:
        raise

    except Exception as e:
        print(
            f"[ADMIN] Erreur suppression utilisateur {user_id} : {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la suppression de l'utilisateur"
        )

@admin_router.post(
    "/users",
    dependencies=[Depends(verify_admin_api_key)]
)
@admin_router.post(
    "/users",
    dependencies=[Depends(verify_admin_api_key)]
)
@admin_router.post(
    "/users",
    dependencies=[Depends(verify_admin_api_key)]
)
def create_admin_user(data: AdminUserCreate):

    try:
        with SessionLocal() as session:

            # Vérification du username
            existing_username = (
                session.query(DBUser)
                .filter(DBUser.username == data.username)
                .first()
            )

            if existing_username:
                raise HTTPException(
                    status_code=409,
                    detail="Ce pseudo est déjà utilisé"
                )

            # Vérification de l'email
            existing_email = (
                session.query(DBUser)
                .filter(DBUser.email == data.email)
                .first()
            )

            if existing_email:
                raise HTTPException(
                    status_code=409,
                    detail="Cette adresse mail est déjà utilisée"
                )

            # Vérification du pepper
            pepper = os.getenv("PEPPER")

            if not pepper:
                raise HTTPException(
                    status_code=500,
                    detail="Configuration PEPPER manquante"
                )

            # Vérification du salt
            if len(data.salt) != 32:
                raise HTTPException(
                    status_code=400,
                    detail="Le salt doit contenir exactement 32 caractères"
                )

            # SHA256(firstHash + salt)
            salted_password = sha256(
                (data.password + data.salt).encode("utf-8")
            ).hexdigest()

            # SHA256(saltedPassword + pepper)
            hashed_password = sha256(
                (salted_password + pepper).encode("utf-8")
            ).hexdigest()


            # Création de l'utilisateur
            now = datetime.datetime.now()

            user = DBUser(
                id=uuid.uuid4(),
                username=data.username,
                email=data.email,
                password=hashed_password,
                birthdate=data.birthdate,
                salt=data.salt,

                is_private=data.is_private,
                history_private=data.history_private,
                adult_content=data.adult_content,
                is_verified=data.is_verified,
                is_admin=data.is_admin,

                country=data.country,
                profile_picture_path=data.profile_picture_path,
                banner_path=data.banner_path,

                last_connection=now,
                created_at=now,

                password_reset_token=None,
                verification_code=None,
                verification_code_token=None,

                country_=None,
                playlist=[],
            )

            session.add(user)

            playlist = DBPlaylist(
                id=uuid.uuid4(),
                user_id=user.id,
                title="Ma playlist",
                is_private=True,
                created_at=now,
                user=user,
            )

            session.add(playlist)

            session.commit()
            session.refresh(user)

            return {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "country": user.country,
                "birthdate": (
                    user.birthdate.isoformat()
                    if user.birthdate
                    else None
                ),
                "profile_picture_path": user.profile_picture_path,
                "banner_path": user.banner_path,
                "is_private": user.is_private,
                "history_private": user.history_private,
                "adult_content": user.adult_content,
                "is_verified": user.is_verified,
                "last_connection": (
                    user.last_connection.isoformat()
                    if user.last_connection
                    else None
                ),
                "created_at": (
                    user.created_at.isoformat()
                    if user.created_at
                    else None
                ),
                "is_admin": user.is_admin,
            }

    except HTTPException:
        raise

    except Exception as e:
        print(f"[ADMIN] Erreur création utilisateur : {e}")

        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la création de l'utilisateur"
        )