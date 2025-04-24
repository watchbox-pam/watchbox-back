from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from domain.interfaces.repositories.i_playlist_repository import IPlaylistRepository
from domain.interfaces.services.i_playlist_service import IPlaylistService
from domain.models.playlist import Playlist
from repository.playlist_repository import PlaylistRepository
from service.playlist_service import PlaylistService

playlist_router = APIRouter(prefix="/playlists", tags=["Playlists"])

def get_playlist_service() -> IPlaylistService:
    repository: IPlaylistRepository = PlaylistRepository()
    return PlaylistService(repository)

@playlist_router.post("/", response_model=bool)
async def create_playlist(playlist: Playlist, service: IPlaylistService = Depends(get_playlist_service)):
    success = service.create_playlist(playlist)
    if not success:
        raise HTTPException(status_code=400, detail="Erreur lors de la création de la playlist")
    return success

@playlist_router.delete("/{playlist_id}", response_model=bool)
async def delete_playlist(playlist_id: int, service: IPlaylistService = Depends(get_playlist_service)):
    success = service.delete_playlist(playlist_id)
    if not success:
        raise HTTPException(status_code=404, detail="Playlist non trouvée")
    return success

@playlist_router.put("/{playlist_id}", response_model=bool)
async def update_playlist(
    playlist_id: int,
    title: Optional[str] = None,
    is_private: Optional[bool] = None,
    service: IPlaylistService = Depends(get_playlist_service)
):
    success = service.update_playlist(playlist_id, title, is_private)
    if not success:
        raise HTTPException(status_code=404, detail="Playlist non trouvée ou mise à jour échouée")
    return success

@playlist_router.get("/{playlist_id}", response_model=Optional[Playlist])
async def get_playlist_by_id(playlist_id: int, service: IPlaylistService = Depends(get_playlist_service)):
    playlist = service.get_playlist_by_id(playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist non trouvée")
    return playlist

@playlist_router.get("/user/{user_id}", response_model=List[Playlist])
async def get_playlists_by_user_id(user_id: str, service: IPlaylistService = Depends(get_playlist_service)):
    playlists = service.get_playlists_by_user_id(user_id)
    return playlists

@playlist_router.post("/{playlist_id}/media/{media_id}", response_model=bool)
async def add_media_to_playlist(
    playlist_id: str,
    media_id: int,
    service: IPlaylistService = Depends(get_playlist_service)
):
    success = service.add_media_to_playlist(playlist_id, media_id)
    if not success:
        raise HTTPException(status_code=400, detail="Erreur lors de l'ajout du média à la playlist")
    return success