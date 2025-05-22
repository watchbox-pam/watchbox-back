from typing import List

from domain.interfaces.repositories.i_playlist_repository import IPlaylistRepository
from domain.interfaces.repositories.i_review_repository import IReviewRepository
from domain.interfaces.services.i_review_service import IReviewService
from domain.models.review import Review


class ReviewService(IReviewService):
    def __init__(self, repository: IReviewRepository, playlist_repository: IPlaylistRepository):
        self.repository = repository
        self.playlist_repository = playlist_repository

    def create_review(self, review: Review) -> bool:
        user_playlists = self.playlist_repository.get_playlists_by_user_id(review.userId)
        user_history_id: str = ""
        for item in user_playlists:
            if item.title == "Historique":
                user_history_id = str(item.id)
                break

        user_history = self.playlist_repository.get_playlist_medias(user_history_id)
        movie_in_history: bool = next((True for ele in user_history if ele.movie_id == review.movieId), False)

        if not movie_in_history:
            self.playlist_repository.add_media_to_playlist(user_history_id, review.movieId)
        review_creation = self.repository.create_review(review)
        return review_creation

    def get_reviews_by_media(self, media_id: int) -> List[Review]:
        return self.repository.get_reviews_by_media(media_id)