from typing import Optional, List
from domain.interfaces.repositories.i_playlist_repository import IPlaylistRepository
from domain.models.playlist import Playlist


class PlaylistService:
    def __init__(self, repository: IPlaylistRepository):
        self.repository = repository

    def create_playlist(self, playlist: Playlist) -> bool:
        return self.repository.create_playlist(playlist)

    def delete_playlist(self, playlist_id: int) -> bool:
        return self.repository.delete_playlist(playlist_id)

    def update_playlist(self, playlist_id: int, title: Optional[str] = None, is_private: Optional[bool] = None) -> bool:
        return self.repository.update_playlist(playlist_id, title, is_private)

    def get_playlist_by_id(self, playlist_id: int) -> Optional[Playlist]:
        return self.repository.get_playlist_by_id(playlist_id)

    def get_playlists_by_user_id(self, user_id: int) -> List[Playlist]:
        return self.repository.get_playlists_by_user_id(user_id)