import uuid

from typing import Optional, List

from fastapi import HTTPException

from domain.interfaces.repositories.i_playlist_repository import IPlaylistRepository
from domain.models.movie import MediaItem
from domain.models.playlist import Playlist


class PlaylistService:
    def __init__(self, repository: IPlaylistRepository):
        self.repository = repository

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
            success = self.repository.add_media_to_playlist(playlist_id, media_id)
            if not success:
                raise HTTPException(status_code=400, detail="Impossible d'ajouter le média à la playlist.")
            return success
        except Exception as e:
            # Lever une exception HTTP avec un message d'erreur
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
        return self.repository.delete_playlist(playlist_id)

    def update_playlist(self, playlist_id: str, title: Optional[str] = None, is_private: Optional[bool] = None) -> bool:
        return self.repository.update_playlist(playlist_id, title, is_private)

    def get_playlist_by_id(self, playlist_id: str) -> Optional[Playlist]:
        return self.repository.get_playlist_by_id(playlist_id)

    def get_playlists_by_user_id(self, user_id: str) -> List[Playlist]:
        return self.repository.get_playlists_by_user_id(user_id)