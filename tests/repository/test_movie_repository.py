import pytest
from unittest.mock import patch, MagicMock

from domain.models.movie import MovieDetail, PopularMovieList
from repository.movie_repository import MovieRepository


# Test de la méthode 'find_by_id' du repository des films
class TestMovieRepository:

    # Patch de la fonction 'call_tmdb_api' pour simuler la réponse de l'API TMDB
    @patch('repository.movie_repository.call_tmdb_api')
    def test_find_by_id(self, mock_call_tmdb_api):
        # Simulation de la réponse de l'API pour un film spécifique
        mock_call_tmdb_api.return_value = {
            "id": 123,
            "adult": False,
            "backdrop_path": "/backdrop.jpg",
            "budget": 10000000,
            "genres": [{"id": 28, "name": "Action"}],
            "original_language": "en",
            "original_title": "Test Movie",
            "overview": "This is a test movie",
            "poster_path": "/poster.jpg",
            "release_date": "2023-01-01",
            "revenue": 20000000,
            "runtime": 120,
            "status": "Released",
            "title": "Test Movie FR",
            "video": False
        }

        # Création de l'objet repository
        repository = MovieRepository()

        # Appel de la méthode find_by_id avec un ID de film
        result = repository.find_by_id(123)

        # Vérification que le résultat est bien une instance de MovieDetail
        assert isinstance(result, MovieDetail)
        assert result.id == 123
        assert result.title == "Test Movie FR"
        assert result.budget == 10000000
        assert result.infos_complete == True

        # Vérification que la méthode de l'API a bien été appelée avec le bon endpoint
        mock_call_tmdb_api.assert_called_once_with("/movie/123?language=fr-FR")

    # Test de la méthode 'search' du repository des films
    @patch('repository.movie_repository.call_tmdb_api')
    def test_search(self, mock_call_tmdb_api):
        # Simulation de la réponse de l'API pour une recherche de film
        mock_call_tmdb_api.return_value = {
            "page": 1,
            "results": [
                {
                    "id": 123,
                    "adult": False,
                    "backdrop_path": "/backdrop.jpg",
                    "original_language": "en",
                    "original_title": "Test Movie",
                    "overview": "This is a test movie",
                    "poster_path": "/poster.jpg",
                    "release_date": "2023-01-01",
                    "title": "Test Movie FR",
                    "video": False
                }
            ],
            "total_pages": 1,
            "total_results": 1
        }

        # Création de l'objet repository
        repository = MovieRepository()

        # Appel de la méthode search pour rechercher un film
        result = repository.search("test movie")

        # Vérification que le nombre de résultats est correct
        assert len(result) == 1
        assert result[0].id == 123
        assert result[0].title == "Test Movie FR"
        assert result[0].infos_complete == True

        # Vérification que la méthode de l'API a bien été appelée avec le bon endpoint
        mock_call_tmdb_api.assert_called_once_with("/search/movie?query=test movie&include_adult=false&language=fr-FR")

    # Test de la méthode 'find_by_time_window' du repository des films
    @patch('repository.movie_repository.call_tmdb_api')
    def test_find_by_time_window(self, mock_call_tmdb_api):
        # Simulation de la réponse de l'API pour les films populaires dans une période donnée
        mock_call_tmdb_api.return_value = {
            "page": 1,
            "results": [
                {
                    "id": 123,
                    "title": "Test Movie",
                    "poster_path": "/poster.jpg"
                }
            ],
            "total_pages": 5,
            "total_results": 100
        }

        # Création de l'objet repository
        repository = MovieRepository()

        # Appel de la méthode find_by_time_window pour récupérer les films populaires
        result = repository.find_by_time_window("week", 1)

        # Vérification que le résultat est une instance de PopularMovieList
        assert isinstance(result, PopularMovieList)
        assert result.page == 1
        assert len(result.results) == 1
        assert result.results[0]["id"] == 123
        assert result.total_pages == 100
        assert result.total_results == 5

        # Vérification que la méthode de l'API a bien été appelée avec le bon endpoint
        mock_call_tmdb_api.assert_called_once_with("/trending/movie/week?page=1")
