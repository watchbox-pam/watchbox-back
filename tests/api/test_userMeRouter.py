import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import Mock

from api.auth.verify_auth_token import check_jwt_token
from api.userMeRouter import get_user_provider_service, user_me_router
from domain.models.providerErrors import InvalidProviderError, ProviderCatalogUnavailableError

USER_ID = "11111111-1111-1111-1111-111111111111"


@pytest.fixture
def service():
    return Mock()


@pytest.fixture
def client(service):
    app = FastAPI()
    app.include_router(user_me_router)
    app.dependency_overrides[check_jwt_token] = lambda: USER_ID
    app.dependency_overrides[get_user_provider_service] = lambda: service
    return TestClient(app)


def test_routes_require_authentication(service):
    app = FastAPI()
    app.include_router(user_me_router)
    app.dependency_overrides[get_user_provider_service] = lambda: service
    anonymous = TestClient(app)

    assert anonymous.get("/users/me/providers").status_code == 401
    assert anonymous.put("/users/me/providers", json={"provider_ids": [8]}).status_code == 401
    assert anonymous.post("/users/me/onboarding/complete").status_code == 401


def test_get_providers(client, service):
    service.get_user_providers.return_value = [{"id": 8, "name": "Netflix", "logo_path": "/n.jpg"}]

    response = client.get("/users/me/providers")

    assert response.status_code == 200
    assert response.json() == [{"id": 8, "name": "Netflix", "logo_path": "/n.jpg"}]
    service.get_user_providers.assert_called_once_with(USER_ID)


def test_put_providers(client, service):
    service.set_user_providers.return_value = [{"id": 8, "name": "Netflix", "logo_path": None}]

    response = client.put("/users/me/providers", json={"provider_ids": [8]})

    assert response.status_code == 200
    service.set_user_providers.assert_called_once_with(USER_ID, [8])


def test_put_providers_unknown_id_returns_400(client, service):
    service.set_user_providers.side_effect = InvalidProviderError([999])

    response = client.put("/users/me/providers", json={"provider_ids": [999]})

    assert response.status_code == 400
    assert "999" in response.json()["detail"]


def test_put_providers_catalog_unavailable_returns_503(client, service):
    service.set_user_providers.side_effect = ProviderCatalogUnavailableError()

    assert client.put("/users/me/providers", json={"provider_ids": [8]}).status_code == 503


def test_put_providers_rejects_invalid_payload(client):
    assert client.put("/users/me/providers", json={"provider_ids": ["netflix"]}).status_code == 422


def test_onboarding_status_and_complete(client, service):
    service.get_onboarding_completed_at.return_value = None
    assert client.get("/users/me/onboarding").json()["onboarding_completed"] is False

    service.complete_onboarding.return_value = datetime.datetime(2026, 11, 24, 21, 0)
    response = client.post("/users/me/onboarding/complete")

    assert response.status_code == 200
    assert response.json()["onboarding_completed"] is True
    service.complete_onboarding.assert_called_once_with(USER_ID)


def test_onboarding_movies_route():
    from api.auth.verify_auth_token import get_adult_content
    from api.userMeRouter import get_onboarding_movie_service
    from domain.models.movie_list_item import MovieListItem

    movie_service = Mock()
    movie_service.get_onboarding_movies.return_value = [MovieListItem(id=1, title="Film", poster_path="/1.jpg")]
    app = FastAPI()
    app.include_router(user_me_router)
    app.dependency_overrides[check_jwt_token] = lambda: USER_ID
    app.dependency_overrides[get_adult_content] = lambda: False
    app.dependency_overrides[get_onboarding_movie_service] = lambda: movie_service
    client = TestClient(app)

    response = client.get("/users/me/onboarding/movies")

    assert response.status_code == 200
    assert response.json() == [{"id": 1, "title": "Film", "poster_path": "/1.jpg"}]
    movie_service.get_onboarding_movies.assert_called_once_with(USER_ID, 15, False)
    assert client.get("/users/me/onboarding/movies?count=100").status_code == 422
