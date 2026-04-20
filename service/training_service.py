from domain.interfaces.repositories.i_recommendation_repository import IRecommendationRepository
from domain.interfaces.repositories.i_playlist_repository import IPlaylistRepository
from service.ml_service import MLService
from service.ml_state import refresh_ml


class TrainingService:
    def __init__(self, recommendation_repo: IRecommendationRepository, playlist_repo: IPlaylistRepository):
        self.recommendation_repo = recommendation_repo
        self.playlist_repo = playlist_repo

    def build_and_train(self) -> MLService:
        print("Récupération des données...")
        ratings = self.recommendation_repo.get_all_reviews()
        implicit_feedback = self.recommendation_repo.get_all_implicit_feedback()
        print(f"{len(ratings)} ratings, {len(implicit_feedback)} feedbacks implicites")
        ml = MLService()
        ml.train(ratings, implicit_feedback)
        ml.save("ml_model.pkl")
        print("Modèle sauvegardé.")
        refresh_ml()
        return ml