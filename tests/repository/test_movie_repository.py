import pytest
from unittest.mock import patch, MagicMock

from domain.models.movie import MovieDetail, PopularMovieList
from repository.movie_repository import MovieRepository


class TestMovieRepository:

    @patch('repository.movie_repository.call_tmdb_api')
    def test_find_by_id(self, mock_call_tmdb_api):
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

        repository = MovieRepository()

        result = repository.find_by_id(123)

        assert isinstance(result, MovieDetail)
        assert result.id == 123
        assert result.title == "Test Movie FR"
        assert result.budget == 10000000
        assert result.infos_complete == True
        mock_call_tmdb_api.assert_called_once_with("/movie/123?language=fr-FR")

    @patch('repository.movie_repository.call_tmdb_api')
    def test_search(self, mock_call_tmdb_api):
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

        repository = MovieRepository()

        result = repository.search("test movie")

        assert len(result) == 1
        assert result[0].id == 123
        assert result[0].title == "Test Movie FR"
        assert result[0].infos_complete == True
        mock_call_tmdb_api.assert_called_once_with("/search/movie?query=test movie&include_adult=false&language=fr-FR")

    @patch('repository.movie_repository.call_tmdb_api')
    def test_find_by_time_window(self, mock_call_tmdb_api):
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

        repository = MovieRepository()

        result = repository.find_by_time_window("week", 1)

        assert isinstance(result, PopularMovieList)
        assert result.page == 1
        assert len(result.results) == 1
        assert result.results[0]["id"] == 123
        assert result.total_pages == 100
        assert result.total_results == 5
        mock_call_tmdb_api.assert_called_once_with("/trending/movie/week?page=1")