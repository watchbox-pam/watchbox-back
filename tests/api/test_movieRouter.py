import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from api.movieRouter import movie_router, get_movie_service
from domain.models.movie import Movie, MovieDetail, PopularMovieList


# Fixture pour simuler le service de films
@pytest.fixture
def mock_movie_service():
    service = Mock()

    # Détail d'un film simulé
    movie_detail = {
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
        "video": False,
        "infos_complete": True,
        "age_restriction": "12",
        "casting": [{"name": "Actor 1", "character": "Character 1"}],
        "director": {"name": "Director"},
        "composer": {"name": "Composer"},
        "video_key": "video_key",
        "providers": [{"provider_id": 1, "provider_name": "Netflix"}]
    }
    # Simulation des retours du service
    service.find_by_id.return_value = movie_detail

    service.search.return_value = [
        Movie(
            id=123,
            adult=False,
            backdrop_path="/backdrop.jpg",
            budget=0,
            original_language="en",
            original_title="Test Movie",
            overview="This is a test movie",
            poster_path="/poster.jpg",
            release_date="2023-01-01",
            revenue=0,
            runtime=0,
            status="",
            title="Test Movie FR",
            video=False,
            infos_complete=True
        )
    ]

    popular_movies = PopularMovieList(
        page=1,
        results=[{
            "id": 123,
            "title": "Test Movie",
            "poster_path": "/poster.jpg"
        }],
        total_pages=5,
        total_results=100
    )
    service.find_by_time_window.return_value = popular_movies

    return service


# Fixture pour l'application FastAPI avec dépendances simulées
@pytest.fixture
def test_app(mock_movie_service):
    app = FastAPI()

    def get_test_movie_service():
        return mock_movie_service

    # Injection de dépendances pour utiliser le service simulé
    app.dependency_overrides[get_movie_service] = get_test_movie_service

    # Middleware pour simuler un utilisateur authentifié
    @app.middleware("http")
    async def mock_auth_middleware(request, call_next):
        request.state.user = {"id": "test-user-id"}
        response = await call_next(request)
        return response

    # Inclure le routeur pour les films
    app.include_router(movie_router)
    return app


# Fixture pour le client de test
@pytest.fixture
def client(test_app):
    return TestClient(test_app)


class TestMovieRouter:

    # Test de la route pour récupérer un film par ID
    def test_get_movie_by_id(self, client, mock_movie_service):
        response = client.get("/movies/id/123")

        # Vérification que la réponse est correcte
        assert response.status_code == 200
        movie_data = response.json()
        assert movie_data["id"] == 123
        assert movie_data["title"] == "Test Movie FR"
        assert movie_data["age_restriction"] == "12"
        assert movie_data["video_key"] == "video_key"
        mock_movie_service.find_by_id.assert_called_once_with(123)

    # Test de la route pour récupérer un film par ID qui n'existe pas
    def test_get_movie_by_id_not_found(self, client, mock_movie_service):
        mock_movie_service.find_by_id.return_value = None

        response = client.get("/movies/id/999")

        # Vérification que la réponse est une erreur 404
        assert response.status_code == 404
        assert response.json()["detail"] == "Movie not found"
        mock_movie_service.find_by_id.assert_called_once_with(999)

    # Test de la route de recherche de films
    def test_search_movies(self, client, mock_movie_service):
        response = client.get("/movies/search/Test%20Movie")

        # Vérification que le film est trouvé et que la recherche retourne le bon résultat
        assert response.status_code == 200
        movies = response.json()
        assert len(movies) == 1
        assert movies[0]["id"] == 123
        assert movies[0]["title"] == "Test Movie FR"
        mock_movie_service.search.assert_called_once_with("Test Movie")

    # Test de la recherche de films qui ne trouve rien
    def test_search_movies_not_found(self, client, mock_movie_service):
        mock_movie_service.search.return_value = None

        response = client.get("/movies/search/NonExistentMovie")

        # Vérification que la recherche retourne une erreur 404
        assert response.status_code == 404
        assert response.json()["detail"] == "Movies not found"
        mock_movie_service.search.assert_called_once_with("NonExistentMovie")

    # Test de la route pour récupérer les films populaires selon une période
    def test_get_movie_by_time_window(self, client, mock_movie_service):
        response = client.get("/movies/popular/week?page=1")

        # Vérification que la réponse est correcte
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["id"] == 123
        mock_movie_service.find_by_time_window.assert_called_once_with("week", 1)

    # Test de la récupération de films populaires selon une période avec un résultat vide
    def test_get_movie_by_time_window_not_found(self, client, mock_movie_service):
        mock_movie_service.find_by_time_window.return_value = None

        response = client.get("/movies/popular/decade")

        # Vérification que la réponse est une erreur 404
        assert response.status_code == 404
        assert response.json()["detail"] == "Movies not found"
        mock_movie_service.find_by_time_window.assert_called_once_with("decade", 1)
