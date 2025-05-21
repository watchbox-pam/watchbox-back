from typing import Optional, List, Protocol

from domain.models.movie import MediaItem, MovieId
from domain.models.playlist import Playlist
from domain.models.playlist_media import PlaylistMedia


class IPlaylistRepository(Protocol):
    def create_playlist(self, playlist: Playlist) -> bool:
        ...

    def create_playlist_on_register(self, user_id: str) -> List[Playlist]:
        ...

    def delete_playlist(self, playlist_id: str) -> bool:
        ...

    def update_playlist(self, playlist_id: str, title: Optional[str] = None, is_private: Optional[bool] = None) -> bool:
        ...

    def get_playlist_by_id(self, playlist_id: str) -> Optional[Playlist]:
        ...

    def get_playlist_medias(self, playlist_id: str) -> Optional[List[PlaylistMedia]]:
        ...

    def get_playlists_by_user_id(self, user_id: str) -> List[Playlist]:
        ...

    def add_media_to_playlist(self, playlist_id: str, media_id: int) -> bool:
        ...

    def media_exists_in_playlist(self, playlist_id: str, media_id: int) -> bool:
        ...

    def get_media_in_playlist(self, playlist_id: str) -> List[MediaItem]:
        ...

    def get_playlist_by_title(self,user_id: str, title: str) -> Optional[Playlist]:
        ...

    def get_movies_from_playlist(self, user_id: str, title: str) -> List[MovieId]:
        ...

    def remove_media_from_playlist(self, playlist_id: str, media_id: int) -> bool:
        ...