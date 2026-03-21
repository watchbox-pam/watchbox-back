import datetime
from typing import Optional, List
import uuid

import db_config
from domain.interfaces.repositories.i_playlist_repository import IPlaylistRepository
from domain.models.playlist import Playlist
from domain.models.movie import MediaItem
from domain.models.playlist_media import PlaylistMedia
from database.db import SessionLocal
from database.models import Playlist as PlaylistModel
from database.models import User
from database.models import t_playlist_media
from database.models import Movie as MovieModel
from sqlalchemy import select, insert, delete

class PlaylistRepository(IPlaylistRepository):
    def create_playlist(self, playlist: Playlist) -> bool:
        success: bool = False

        try:
            with SessionLocal() as session:
                user = session.query(User).filter(User.id == playlist.user_id).first()

                new_playlist = PlaylistModel(
                    id=playlist.id,
                    user_id=playlist.user_id,
                    title=playlist.title,
                    created_at=datetime.datetime.now(datetime.UTC),
                    is_private=playlist.is_private,
                    user=user
                )
                session.add(new_playlist)
                session.commit()
                success = True

        except Exception as e:
            print(e)

        return success

    def create_playlist_on_register(self, user_id: str) -> List[Playlist]:
        playlists = [
            Playlist(
                id=str(uuid.uuid4()),
                user_id=user_id,
                title="Favoris",
                created_at=datetime.datetime.utcnow(),
                is_private=True
            ),
            Playlist(
                id=str(uuid.uuid4()),
                user_id=user_id,
                title="Historique",
                created_at=datetime.datetime.utcnow(),
                is_private=True
            ),
            Playlist(
                id=str(uuid.uuid4()),
                user_id=user_id,
                title="Watchlist",
                created_at=datetime.datetime.utcnow(),
                is_private=True
            ),
        ]

        for playlist in playlists:
            self.create_playlist(playlist)

        return playlists

    def delete_playlist(self, playlist_id: str) -> bool:
        success: bool = False

        try:
            with SessionLocal() as session:
                playlist = session.query(PlaylistModel).filter(PlaylistModel.id == playlist_id).first()
                if playlist:
                    session.delete(playlist)
                    session.commit()
                    success = True

        except Exception as e:
            print(e)

        return success

    def update_playlist(self, playlist_id: str, title: Optional[str] = None, is_private: Optional[bool] = None) -> bool:
        success: bool = False

        try:
            with SessionLocal() as session:
                playlist = session.query(PlaylistModel).filter(PlaylistModel.id == playlist_id).first()
                
                if playlist is None:
                    return False

                if title is not None:
                    playlist.title = title
                if is_private is not None:
                    playlist.is_private = is_private

                session.commit()
                success = True

        except Exception as e:
            print(f"Erreur lors de la mise à jour de la playlist : {e}")

        return success

    def get_playlist_by_id(self, playlist_id: str) -> Optional[Playlist]:
        playlist: Optional[Playlist] = None

        try:
            with SessionLocal() as session:
                result = session.query(PlaylistModel).filter(PlaylistModel.id == playlist_id).first()

                if result is not None:
                    playlist = Playlist(
                        id=str(result.id),
                        user_id=str(result.user_id),
                        title=result.title,
                        is_private=result.is_private,
                        created_at=result.created_at,
                    )

        except Exception as e:
            print(e)

        return playlist

    def get_playlist_medias(self, playlist_id: str) -> Optional[List[Playlist]]:
        medias = []

        try:            
            with SessionLocal() as session:
                results = session.execute(
                    select(t_playlist_media).where(t_playlist_media.c.playlist_id == playlist_id)
                ).fetchall()

                for result in results:
                    medias.append(PlaylistMedia(
                        playlist_id=result.playlist_id,
                        movie_id=result.movie_id,
                        tv_id=result.tv_id,
                        add_date=result.add_date,
                    ))  

        except Exception as e:
            print(e)

        return medias

    def get_playlists_by_user_id(self, user_id: str) -> List[Playlist]:
        playlists: List[Playlist] = []

        try:
            with SessionLocal() as session:
                results = session.query(PlaylistModel).filter(PlaylistModel.user_id == user_id).all()

                for result in results:
                    playlists.append(Playlist(
                        id=str(result.id),
                        user_id=str(result.user_id),
                        title=result.title,
                        created_at=result.created_at,
                        is_private=result.is_private
                    ))

        except Exception as e:
            print(e)

        return playlists

    def add_media_to_playlist(self, playlist_id: str, media_id: int) -> bool:
        success: bool = False

        try:
            with SessionLocal() as session:
                session.execute(
                    insert(t_playlist_media).values(
                        playlist_id=playlist_id,
                        movie_id=media_id,
                        add_date=datetime.datetime.now()
                    )
                )
                session.commit()
                success = True

        except Exception as e:
            print(e)

        return success

    def media_exists_in_playlist(self, playlist_id: str, media_id: int) -> bool:
        try:            
            with SessionLocal() as session:
                result = session.execute(
                    select(t_playlist_media).where(
                        (t_playlist_media.c.playlist_id == playlist_id) &
                        (t_playlist_media.c.movie_id == media_id)
                    )
                ).fetchone()
                return result is not None
        except Exception as e:
            return False

    def get_media_in_playlist(self, playlist_id: str) -> list[MediaItem]:
        media_data: list[MediaItem] = []

        try:
            with SessionLocal() as session:                

                results = session.execute(
                    select(
                        MovieModel.id,
                        MovieModel.poster_path
                ).select_from(
                        t_playlist_media.join(
                            MovieModel, t_playlist_media.c.movie_id == MovieModel.id
                        ).join(
                            PlaylistModel, t_playlist_media.c.playlist_id == PlaylistModel.id
                        )
                    ).where(PlaylistModel.id == playlist_id)
                ).fetchall()

                for result in results:
                    media_data.append(MediaItem(
                        id=result.id,
                        image=result.poster_path
                    ))

        except Exception as e:
            print(e)

        return media_data

    def remove_media_from_playlist(self, playlist_id: str, media_id: int) -> bool:
        success: bool = False

        try:
            with SessionLocal() as session:
                result = session.execute(
                    delete(t_playlist_media).where(
                        (t_playlist_media.c.playlist_id == playlist_id) &
                        (t_playlist_media.c.movie_id == media_id)
                    )
                )
                session.commit()
                success = result.rowcount > 0

        except Exception as e:
            print(e)

        return success