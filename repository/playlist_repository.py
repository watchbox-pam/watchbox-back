import datetime
from typing import Optional, List
import uuid
import pandas as pd
import zipfile

from domain.interfaces.repositories.i_playlist_repository import IPlaylistRepository
from domain.models.playlist import Playlist
from domain.models.movie import MediaItem
from domain.models.playlist_media import PlaylistMedia
from database.db import SessionLocal
from database.models import Playlist as DBPlaylist
from database.models import User as DBUser
from database.models import t_playlist_media
from database.models import Movie as DBMovie
from sqlalchemy import select, insert, delete, update, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from utils.tmdb_service import call_tmdb_api
from domain.models.playlist import ImportProvider

class PlaylistRepository(IPlaylistRepository):
    def create_playlist(self, playlist: Playlist) -> bool:
        success: bool = False

        try:
            with SessionLocal() as session:
                user = session.query(DBUser).filter(DBUser.id == playlist.user_id).first()

                new_playlist = DBPlaylist(
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
                playlist = session.query(DBPlaylist).filter(DBPlaylist.id == playlist_id).first()
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
                playlist = session.query(DBPlaylist).filter(DBPlaylist.id == playlist_id).first()
                
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
                result = session.query(DBPlaylist).filter(DBPlaylist.id == playlist_id).first()

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
                results = session.query(DBPlaylist).filter(DBPlaylist.user_id == user_id).all()

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
                movie_exists = session.query(DBMovie.id).filter(DBMovie.id == media_id).first()
                if not movie_exists:
                    tmdb = call_tmdb_api(f"/movie/{media_id}?language=fr-FR")
                    release_date_str = tmdb.get("release_date", "")
                    release_date = datetime.date.fromisoformat(release_date_str) if release_date_str else None
                    session.execute(
                        pg_insert(DBMovie).values(
                            id=tmdb["id"],
                            title=tmdb.get("title"),
                            poster_path=tmdb.get("poster_path"),
                            backdrop_path=tmdb.get("backdrop_path"),
                            overview=tmdb.get("overview"),
                            release_date=release_date,
                            adult=tmdb.get("adult"),
                            original_language=tmdb.get("original_language"),
                            original_title=tmdb.get("original_title"),
                            runtime=tmdb.get("runtime"),
                            popularity=tmdb.get("popularity"),
                            infos_complete=False,
                        ).on_conflict_do_nothing(index_elements=["id"])
                    )

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

    def touch_media_in_playlist(self, playlist_id: str, media_id: int) -> bool:
        """Refresh add_date to now() so an already-present movie moves back to the
        top of the playlist (most-recent-first ordering) without inserting a duplicate."""
        success: bool = False
        try:
            with SessionLocal() as session:
                session.execute(
                    update(t_playlist_media)
                    .where(
                        (t_playlist_media.c.playlist_id == playlist_id) &
                        (t_playlist_media.c.movie_id == media_id)
                    )
                    .values(add_date=datetime.datetime.now())
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
                        DBMovie.id,
                        DBMovie.poster_path,
                        DBMovie.title,
                        DBMovie.release_date,
                ).select_from(
                        t_playlist_media.join(
                            DBMovie, t_playlist_media.c.movie_id == DBMovie.id
                        ).join(
                            DBPlaylist, t_playlist_media.c.playlist_id == DBPlaylist.id
                        )
                    ).where(DBPlaylist.id == playlist_id)
                    .order_by(t_playlist_media.c.add_date.desc().nulls_last())
                ).fetchall()

                for result in results:
                    media_data.append(MediaItem(
                        id=result.id,
                        image=result.poster_path,
                        title=result.title,
                        release_date=result.release_date,
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

    def add_file_to_watchlist(self, user_id, file, import_id) -> bool:
        try:
            movie_names = []

            match import_id:
                case ImportProvider.LETTERBOXD.value:
                    if file.content_type != "application/zip":
                        raise Exception("Le fichier doit être un fichier zip pour l'import Letterboxd.")
                    with zipfile.ZipFile(file.file) as z:
                        # look for file "watched.csv" in the zip
                        if "watched.csv" in z.namelist():
                            with z.open("watched.csv") as f:
                                extracted_data = pd.read_csv(f, usecols=[1], skiprows=1)
                                movie_names = (
                                    extracted_data.iloc[:, 0]
                                    .str.replace("\xa0", " ", regex=False)
                                    .str.strip()
                                )
                        else:
                            raise Exception("Le fichier zip ne contient pas 'watched.csv'.")

                case ImportProvider.NETFLIX.value:   
                    if file.content_type != "text/comma-separated-values":
                        raise Exception("Le fichier doit être un fichier CSV pour l'import Netflix.")
                    extracted_data = pd.read_csv(file.file, usecols=[0], skiprows=1)
                    movie_names = (
                        extracted_data.iloc[:, 0]
                        .str.replace("\xa0", " ", regex=False)
                        .str.strip()
                    )
                    movie_names = [name for name in movie_names.tolist() if name]
            
            with SessionLocal() as session:

                # Get the watchlist playlist for the current user
                watchlist_playlist = session.query(DBPlaylist).filter(
                    DBPlaylist.user_id == user_id,
                    DBPlaylist.title == "Watchlist"
                ).first()

                if not watchlist_playlist:
                    raise Exception("Watchlist playlist not found for the current user.")

                movie_ids = []
                for movie_name in movie_names:
                    # Search for the movie in the database
                    movie = session.query(DBMovie).filter(
                        (DBMovie.title.ilike(f"%{movie_name}%")) |
                        (DBMovie.original_title.ilike(f"%{movie_name}%"))
                    ).first()

                    if movie:
                        movie_ids.append(movie.id)
                    """ else:
                        # If the movie is not found, you can choose to log it or handle it as needed
                        print(f"Not found movie '{movie_name}' in the database.") """

                # Add the found movie IDs to the watchlist playlist
                for movie_id in movie_ids:
                    session.execute(
                        pg_insert(t_playlist_media).values(
                            playlist_id=watchlist_playlist.id,
                            movie_id=movie_id,
                            add_date=datetime.datetime.now()
                        ).on_conflict_do_nothing(
                            index_elements=["playlist_id", "movie_id"],
                            index_where=text("movie_id IS NOT NULL")
                        )
                    )

                session.commit()

                return True
        except Exception as e:
            print(e)

        return False