import datetime
from typing import Optional, List

import db_config
from domain.models.playlist import Playlist


class PlaylistRepository:
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

    def delete_playlist(self, playlist_id: int) -> bool:
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

    def update_playlist(self, playlist_id: int, title: Optional[str] = None, is_private: Optional[bool] = None) -> bool:
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

    def get_playlist_by_id(self, playlist_id: int) -> Optional[Playlist]:
        playlist: Optional[Playlist] = None

        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM public.playlist WHERE id=%s;", (playlist_id,))
                    result = cur.fetchone()

                    if result is not None:
                        playlist = Playlist(
                            id=result[0],
                            user_id=result[1],
                            title=result[2],
                            created_at=result[3],
                            is_private=result[4],
                        )

        except Exception as e:
            print(e)

        return playlist

    def get_playlists_by_user_id(self, user_id: int) -> List[Playlist]:
        playlists: List[Playlist] = []

        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM public.playlist WHERE user_id=%s;", (user_id,))
                    results = cur.fetchall()

                    for result in results:
                        playlists.append(Playlist(
                            id=result[0],
                            user_id=result[1],
                            title=result[2],
                            created_at=result[3],
                            is_private=result[4],
                        ))

        except Exception as e:
            print(e)

        return playlists