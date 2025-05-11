import datetime
from typing import Optional, List
import uuid

import db_config
from domain.interfaces.repositories.i_playlist_repository import IPlaylistRepository
from domain.models.playlist import Playlist
from domain.models.movie import MediaItem
from domain.models.playlist_media import PlaylistMedia


class PlaylistRepository(IPlaylistRepository):
    def create_playlist(self, playlist: Playlist) -> bool:
        success: bool = False

        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    query = ("INSERT INTO public.playlist "
                             "(id, user_id, title, created_at, is_private) "
                             "VALUES (%s, %s, %s, %s, %s);")

                    values = (playlist.id, playlist.user_id, playlist.title, datetime.datetime.now(datetime.UTC), playlist.is_private)

                    cur.execute(query, values)
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
            )
        ]

        for playlist in playlists:
            self.create_playlist(playlist)

        return playlists

    def delete_playlist(self, playlist_id: str) -> bool:
        success: bool = False

        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    query = "DELETE FROM public.playlist WHERE id=%s;"
                    cur.execute(query, (playlist_id,))
                    success = cur.rowcount > 0

        except Exception as e:
            print(e)

        return success

    def update_playlist(self, playlist_id: str, title: Optional[str] = None, is_private: Optional[bool] = None) -> bool:
        success: bool = False

        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    updates = []
                    values = []

                    if title is not None:
                        updates.append("title=%s")
                        values.append(title)

                    if is_private is not None:
                        updates.append("is_private=%s")
                        values.append(is_private)

                    if updates:
                        query = f"UPDATE public.playlist SET {', '.join(updates)} WHERE id=%s;"
                        values.append(playlist_id)
                        cur.execute(query, tuple(values))
                        success = cur.rowcount > 0

        except Exception as e:
            print(e)

        return success

    def get_playlist_by_id(self, playlist_id: str) -> Optional[Playlist]:
        playlist: Optional[Playlist] = None

        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM public.playlist WHERE id=%s;", (playlist_id,))
                    result = cur.fetchone()

                    if result is not None:
                        playlist = Playlist(
                            id=str(result[0]),
                            user_id=str(result[1]),
                            title=result[2],
                            is_private=result[3],
                            created_at=result[4],
                        )

        except Exception as e:
            print(e)

        return playlist

    def get_playlist_medias(self, playlist_id: str) -> Optional[List[Playlist]]:
        medias = []

        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM public.playlist_media WHERE playlist_id=%s;", (playlist_id,))
                    results = cur.fetchall()

                    if results is not None:
                        for result in results:
                            medias.append(PlaylistMedia(
                                playlist_id=result[0],
                                movie_id=result[1],
                                tv_id=result[2],
                                add_date=result[3],
                            ))

        except Exception as e:
            print(e)

        return medias

    def get_playlists_by_user_id(self, user_id: str) -> List[Playlist]:
        playlists: List[Playlist] = []

        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM public.playlist WHERE user_id=%s;", (user_id,))
                    results = cur.fetchall()

                    for result in results:
                        playlists.append(Playlist(
                            id=str(result[0]),
                            user_id=str(result[1]),
                            title=result[2],
                            is_private=result[3],
                            created_at=result[4],
                        ))

        except Exception as e:
            print(e)

        return playlists

    def add_media_to_playlist(self, playlist_id: str, media_id: int) -> bool:
        success: bool = False

        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:

                    query = "INSERT INTO public.playlist_media (playlist_id, movie_id, add_date) VALUES (%s, %s, %s);"
                    add_date = datetime.datetime.now()
                    cur.execute(query, (playlist_id, media_id, add_date))
                    success = True

        except Exception as e:
            print(e)

        return success

    def get_media_in_playlist(self, playlist_id: str) -> list[MediaItem]:
        media_data: list[MediaItem] = []

        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    query = """
                        SELECT m.id, m.poster_path
                        FROM public.playlist_media pm
                        JOIN public.movie m ON pm.movie_id = m.id
                        WHERE pm.playlist_id = %s;
                    """
                    cur.execute(query, (playlist_id,))
                    results = cur.fetchall()

                    for result in results:
                        media_data.append(MediaItem(
                            id=result[0],
                            image=result[1]
                        ))

        except Exception as e:
            print(e)

        return media_data

    def remove_media_from_playlist(self, playlist_id: str, media_id: int) -> bool:
        success: bool = False

        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    query = "DELETE FROM public.playlist_media WHERE playlist_id=%s AND movie_id=%s;"
                    cur.execute(query, (playlist_id, media_id))
                    success = cur.rowcount > 0

        except Exception as e:
            print(e)

        return success