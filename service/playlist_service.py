import uuid
import logging

# Configuration de base du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from typing import Optional, List
from datetime import datetime

from fastapi import HTTPException

from domain.interfaces.repositories.i_playlist_repository import IPlaylistRepository
from domain.models.movie import MediaItem, MovieId
from domain.interfaces.repositories.i_movie_repository import IMovieRepository
from domain.interfaces.services.i_playlist_service import IPlaylistService
from domain.models.playlist import Playlist
from domain.models.playlist_media import PlaylistMedia


class PlaylistService(IPlaylistService):
    def __init__(self, repository: IPlaylistRepository, movie_repository: Optional[IMovieRepository] = None):
        self.repository = repository
        self.movie_repository = movie_repository

    def create_playlist(self, playlist: Playlist) -> bool:
        existing_playlists = self.repository.get_playlists_by_user_id(playlist.user_id)
        if any(p.title == playlist.title for p in existing_playlists):
            raise HTTPException(status_code=400, detail="Playlist déjà existante pour cet utilisateur.")

        playlist_id: str = str(uuid.uuid4())
        new_playlist = Playlist(
            id=playlist_id,
            user_id=playlist.user_id,
            title=playlist.title,
            created_at=playlist.created_at,
            is_private=playlist.is_private
        )
        return self.repository.create_playlist(new_playlist)

    def add_media_to_playlist(self, playlist_id: str, media_id: int) -> bool:
        try:

            if self.repository.media_exists_in_playlist(playlist_id, media_id):
                raise HTTPException(status_code=400, detail="Le média est déjà présent dans la playlist.")

            success = self.repository.add_media_to_playlist(playlist_id, media_id)
            if not success:
                raise HTTPException(status_code=400, detail="Impossible d'ajouter le média à la playlist.")
            return success
        except Exception as e:

            raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")

    def get_media_in_playlist(self, playlist_id: str) -> List[MediaItem]:
        try:
            media_list = self.repository.get_media_in_playlist(playlist_id)
            if not media_list:
                raise HTTPException(status_code=404, detail="Aucun média trouvé dans cette playlist.")
            return media_list
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")

    def delete_playlist(self, playlist_id: str) -> bool:
        existing_playlist = self.repository.get_playlist_by_id(playlist_id)
        if not existing_playlist:
            raise HTTPException(status_code=404, detail="Playlist introuvable.")
        success = self.repository.delete_playlist(playlist_id)
        if not success:
            raise HTTPException(status_code=400, detail="Erreur lors de la suppression de la playlist.")
        return success

    def update_playlist(self, playlist_id: str,user_id: str, title: Optional[str] = None, is_private: Optional[bool] = None) -> bool:
        try:
            if title:
                current = self.repository.get_playlist_by_id(playlist_id)
                if not current:
                    raise HTTPException(status_code=404, detail="Playlist introuvable.")
                if title != current.title:
                    existing_playlists = self.repository.get_playlists_by_user_id(user_id)
                    if any(p.title.lower() == title.lower() for p in existing_playlists):
                        raise HTTPException(status_code=400, detail="Playlist déjà existante pour cet utilisateur.")
            success = self.repository.update_playlist(playlist_id, title, is_private)
            if not success:
                raise HTTPException(status_code=404, detail="Playlist introuvable ou aucune mise à jour effectuée.")
            return success
        except HTTPException as http_exc:
                raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")

    def get_playlist_by_id(self, playlist_id: str) -> Optional[Playlist]:
        return self.repository.get_playlist_by_id(playlist_id)

    def get_playlist_medias(self, playlist_id: str) -> Optional[List[PlaylistMedia]]:
        return self.repository.get_playlist_medias(playlist_id)

    def get_playlists_by_user_id(self, user_id: str) -> List[Playlist]:
        return self.repository.get_playlists_by_user_id(user_id)

    def remove_media_from_playlist(self, playlist_id: str, media_id: int) -> bool:
        try:
            success = self.repository.remove_media_from_playlist(playlist_id, media_id)
            if not success:
                raise HTTPException(status_code=400, detail="Impossible de retirer le média de la playlist.")
            return success
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")

    def get_movie_runtime_by_playlist_title(self, user_id: str, title: str) -> dict[str, int]:
        try:
            logger.info(f"Récupération des films pour la playlist '{title}' et l'utilisateur '{user_id}'")
            movies = self.repository.get_movies_from_playlist(user_id, title)
            if not movies:
                logger.error("Aucun film trouvé dans la playlist.")
                raise HTTPException(status_code=404, detail="Aucun média trouvé dans cette playlist.")

            movie_ids = [movie.id for movie in movies]
            movie_count = len(movie_ids)
            logger.info(f"IDs des films récupérés : {movie_ids}")

            total_runtime = self.movie_repository.movie_runtime(movie_ids)
            if total_runtime is None:
                logger.error("Durée totale des films introuvable.")
                raise HTTPException(status_code=500, detail="Erreur lors du calcul de la durée totale des films.")

            return {"total_runtime": total_runtime, "movie_count": movie_count}
        except Exception as e:
            logger.error(f"Erreur interne : {e}")
            raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")