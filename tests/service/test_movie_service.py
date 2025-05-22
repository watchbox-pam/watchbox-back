import pytest
from unittest.mock import Mock, patch

from domain.models.movie import Movie, MovieDetail, PopularMovieList
from service.movie_service import MovieService


# Fixture pour simuler le repository des films
@pytest.fixture
def mock_movie_repository():
    repository = Mock()

    # Détail d'un film pour simuler la méthode 'find_by_id'
    movie_detail = MovieDetail(
        id=123,
        adult=False,
        backdrop_path="/backdrop.jpg",
        budget=10000000,
        genres=[{"id": 28, "name": "Action"}],
        original_language="en",
        original_title="Test Movie",
        overview="This is a test movie",
        poster_path="/poster.jpg",
        release_date="2023-01-01",
        revenue=20000000,
        runtime=120,
        status="Released",
        title="Test Movie FR",
        video=False,
        infos_complete=True
    )
    repository.find_by_id.return_value = movie_detail  # Simuler la réponse de 'find_by_id'

    # Liste de films pour simuler la méthode 'search'
    repository.search.return_value = [
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

    # Liste de films populaires pour simuler 'find_by_time_window'
    popular_movies = PopularMovieList(
        page=1,
        results=[{
            "id": 123,
            "title": "Test Movie",
            "poster_path": "/poster.jpg"
        }],
        total_pages=10,
        total_results=200
    )
    repository.find_by_time_window.return_value = popular_movies  # Simuler la réponse de films populaires

    return repository


# Fixture pour simuler le repository des dates de sortie
@pytest.fixture
def mock_release_dates_repository():
    repository = Mock()
    repository.find_by_id.return_value = Mock(
        results=[
            {
                "iso_3166_1": "FR",
                "release_dates": [
                    {"type": 3, "certification": "12"}
                ]
            }
        ]
    )
    return repository


# Fixture pour simuler le repository des crédits (acteurs, réalisateur)
@pytest.fixture
def mock_credits_repository():
    repository = Mock()
    repository.find_by_id.return_value = Mock(
        cast=[
            {"name": "Actor 1", "character": "Character 1"},
            {"name": "Actor 2", "character": "Character 2"}
        ],
        crew=[
            {"name": "Director", "known_for_department": "Directing"},
            {"name": "Composer", "known_for_department": "Sound"}
        ]
    )
    return repository


# Fixture pour simuler le repository des vidéos (par exemple, YouTube)
@pytest.fixture
def mock_videos_repository():
    repository = Mock()
    repository.find_by_id.return_value = Mock(
        results=[
            {"site": "YouTube", "type": "Trailer", "key": "video_key"}
        ]
    )
    return repository


# Fixture pour simuler le repository des fournisseurs de diffusion (Netflix, etc.)
@pytest.fixture
def mock_watch_providers_repository():
    repository = Mock()
    repository.find_by_id.return_value = Mock(
        results={
            "FR": {
                "flatrate": [
                    {"provider_id": 1, "provider_name": "Netflix"}
                ]
            }
        }
    )
    return repository


# Tests de la classe MovieService
class TestMovieService:

    # Test de la méthode 'find_by_id' pour récupérer un film par son ID
    def test_find_by_id(self, mock_movie_repository, mock_release_dates_repository,
                        mock_credits_repository, mock_videos_repository,
                        mock_watch_providers_repository):
        service = MovieService(
            mock_movie_repository,
            mock_release_dates_repository,
            mock_credits_repository,
            mock_videos_repository,
            mock_watch_providers_repository
        )

        result = service.find_by_id(123)

        # Vérification que les données du film sont correctes
        assert result["id"] == 123
        assert result["title"] == "Test Movie FR"
        assert result["age_restriction"] == "12"
        assert result["video_key"] == "video_key"
        assert result["director"]["name"] == "Director"
        assert result["composer"]["name"] == "Composer"
        mock_movie_repository.find_by_id.assert_called_once_with(123)
        mock_release_dates_repository.find_by_id.assert_called_once_with(123)
        mock_credits_repository.find_by_id.assert_called_once_with(123)
        mock_videos_repository.find_by_id.assert_called_once_with(123)
        mock_watch_providers_repository.find_by_id.assert_called_once_with(123)

    # Test de la méthode 'search' pour rechercher des films
    def test_search(self, mock_movie_repository, mock_release_dates_repository,
                    mock_credits_repository, mock_videos_repository,
                    mock_watch_providers_repository):

        service = MovieService(
            mock_movie_repository,
            mock_release_dates_repository,
            mock_credits_repository,
            mock_videos_repository,
            mock_watch_providers_repository
        )

        result = service.search("Test Movie")

        # Vérification que la recherche a retourné un film
        assert len(result) == 1
        assert result[0].id == 123
        assert result[0].title == "Test Movie FR"
        mock_movie_repository.search.assert_called_once_with("Test Movie")

    # Test de la méthode 'find_by_time_window' pour récupérer les films populaires
    def test_find_by_time_window(self, mock_movie_repository, mock_release_dates_repository,
                                 mock_credits_repository, mock_videos_repository,
                                 mock_watch_providers_repository):
        service = MovieService(
            mock_movie_repository,
            mock_release_dates_repository,
            mock_credits_repository,
            mock_videos_repository,
            mock_watch_providers_repository
        )

        result = service.find_by_time_window("week", 1)

        # Vérification des films populaires retournés
        assert result.page == 1
        assert len(result.results) == 1
        assert result.results[0]["id"] == 123
        mock_movie_repository.find_by_time_window.assert_called_once_with("week", 1)