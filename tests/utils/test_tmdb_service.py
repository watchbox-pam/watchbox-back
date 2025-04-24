import pytest
from unittest.mock import patch, MagicMock
import json
import os
from utils.tmdb_service import call_tmdb_api


@patch('utils.tmdb_service.requests.get')
def test_call_tmdb_api(mock_get):
    mock_response = MagicMock()
    mock_response.text = json.dumps({"id": 123, "title": "Test Movie"})
    mock_get.return_value = mock_response

    result = call_tmdb_api("/movie/123")

    assert result["id"] == 123
    assert result["title"] == "Test Movie"

    expected_url = os.getenv("TMDB_BASE_URL") + "/movie/123"
    expected_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.getenv('TMDB_API_KEY')}"
    }
    mock_get.assert_called_once_with(expected_url, headers=expected_headers)


@patch('utils.tmdb_service.requests.get')
@pytest.mark.parametrize("endpoint,expected_id", [
    ("/movie/123", 123),
    ("/tv/456", 456),
    ("/person/789", 789)
])
def test_call_tmdb_api_with_different_endpoints(mock_get, endpoint, expected_id):
    mock_response = MagicMock()
    mock_response.text = json.dumps({"id": expected_id})
    mock_get.return_value = mock_response

    result = call_tmdb_api(endpoint)

    assert result["id"] == expected_id


@patch('utils.tmdb_service.requests.get')
def test_call_tmdb_api_with_error_response(mock_get):
    mock_response = MagicMock()
    mock_response.text = json.dumps({"status_code": 404, "status_message": "Not Found"})
    mock_get.return_value = mock_response

    result = call_tmdb_api("/movie/999999")

    assert "status_code" in result
    assert result["status_code"] == 404


@patch('utils.tmdb_service.os.getenv')
@patch('utils.tmdb_service.requests.get')
def test_call_tmdb_api_with_missing_env_variables(mock_get, mock_getenv):
    def mock_getenv_side_effect(key):
        if key == "TMDB_API_KEY":
            return None
        return "https://api.themoviedb.org/3"

    mock_getenv.side_effect = mock_getenv_side_effect
    mock_response = MagicMock()
    mock_response.text = json.dumps({"success": False})
    mock_get.return_value = mock_response

    result = call_tmdb_api("/movie/123")
    assert isinstance(result, dict)