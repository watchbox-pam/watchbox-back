import pytest
from unittest.mock import patch, MagicMock
import json
import requests
from utils.tmdb_service import call_tmdb_api


# on vérifie qu'un appel API réussi renvoie bien les données attendues
# On mock la requête HTTP pour ne pas appeler TMDB réellement
@patch('utils.tmdb_service.requests.get')
def test_call_tmdb_api_success(mock_get):
    mock_response = MagicMock()
    mock_response.text = json.dumps({"id": 123, "title": "Test Movie"})
    mock_get.return_value = mock_response

    result = call_tmdb_api("/movie/123")

    assert result["id"] == 123
    assert result["title"] == "Test Movie"


# Test paramétré : on teste différents endpoints (films, séries, personnes)
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


# Test d’un retour d’erreur normal de l’API (ex : 404 Not Found)
@patch('utils.tmdb_service.requests.get')
def test_call_tmdb_api_with_error_response(mock_get):
    mock_response = MagicMock()
    mock_response.text = json.dumps({"status_code": 404, "status_message": "Not Found"})
    mock_get.return_value = mock_response

    # Film inexistant
    result = call_tmdb_api("/movie/999999")

    assert "status_code" in result
    assert result["status_code"] == 404


# Test d’un retour de réponse illisible (ex : JSON cassé)
@patch('utils.tmdb_service.requests.get')
def test_call_tmdb_api_invalid_json(mock_get):
    mock_response = MagicMock()

    # Simule un corps de réponse invalide
    mock_response.text = "INVALID_JSON"
    mock_get.return_value = mock_response

    result = call_tmdb_api("/movie/invalid")
    assert "error" in result
    assert result["error"] == "Invalid JSON response"


# Test en cas d’erreur réseau simulée
@patch('utils.tmdb_service.requests.get')
def test_call_tmdb_api_network_error(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("Network error")

    result = call_tmdb_api("/movie/network-error")
    assert "error" in result
    assert "Network error" in result["error"]


# Test si la variable d’environnement TMDB_BASE_URL est manquante
@patch('utils.tmdb_service.os.getenv')
@patch('utils.tmdb_service.requests.get')
def test_call_tmdb_api_missing_base_url(mock_get, mock_getenv):

    # On simule une absence de la variable TMDB_BASE_URL
    def getenv_side_effect(key):
        if key == "TMDB_BASE_URL":
            return None
        return "fake-token"
    mock_getenv.side_effect = getenv_side_effect

    result = call_tmdb_api("/movie/123")
    assert "error" in result
    assert result["error"] == "Missing TMDB_BASE_URL or TMDB_API_KEY"


#Test si la variable d’environnement TMDB_API_KEY est manquante
@patch('utils.tmdb_service.os.getenv')
@patch('utils.tmdb_service.requests.get')
def test_call_tmdb_api_missing_api_key(mock_get, mock_getenv):

    # On simule une absence de la variable TMDB_API_KEY
    def getenv_side_effect(key):
        if key == "TMDB_API_KEY":
            return None
        return "https://api.themoviedb.org/3"
    mock_getenv.side_effect = getenv_side_effect

    result = call_tmdb_api("/movie/123")

    assert "error" in result
    assert result["error"] == "Missing TMDB_BASE_URL or TMDB_API_KEY"
