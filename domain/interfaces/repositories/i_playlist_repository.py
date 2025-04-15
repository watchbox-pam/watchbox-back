from typing import Optional, List, Protocol
from domain.models.playlist import Playlist

class IPlaylistRepository(Protocol):
    def create_playlist(self, playlist: Playlist) -> bool:
        ...

    def delete_playlist(self, playlist_id: int) -> bool:
        ...

    def update_playlist(self, playlist_id: int, title: Optional[str] = None, is_private: Optional[bool] = None) -> bool:
        ...

    def get_playlist_by_id(self, playlist_id: int) -> Optional[Playlist]:
        ...

    def get_playlists_by_user_id(self, user_id: int) -> List[Playlist]:
        ...