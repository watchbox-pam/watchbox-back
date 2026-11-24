from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.admin.movies import router, get_admin_movie_service
from service.admin_movie_service import AdminMovieService


def _db_movie(**overrides):
    base = dict(
        id=123, title="Test", poster_path=None, release_date=None,
        popularity=None, runtime=None, infos_complete=False, adult=False, video=None,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def client(repository):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_admin_movie_service] = lambda: AdminMovieService(repository)
    return TestClient(app)


@pytest.mark.parametrize("sent, expected", [(True, True), (False, False), ("true", True), ("false", False)])
def test_create_movie_video_is_bool(client, repository, sent, expected):
    repository.find_by_id.return_value = None
    repository.create.side_effect = lambda data: _db_movie(**data)

    response = client.post("/movies", json={"id": 123, "title": "Test", "video": sent})

    assert response.status_code == 200
    assert repository.create.call_args.args[0]["video"] is expected


@pytest.mark.parametrize("sent, expected", [(True, True), (False, False), ("1", True), ("0", False)])
def test_update_movie_video_is_bool(client, repository, sent, expected):
    repository.update.side_effect = lambda movie_id, data: _db_movie(id=movie_id, **data)

    response = client.put("/movies/123", json={"video": sent})

    assert response.status_code == 200
    assert repository.update.call_args.args[1] == {"video": expected}


def test_create_movie_rejects_non_boolean_video(client, repository):
    repository.find_by_id.return_value = None

    response = client.post("/movies", json={"id": 123, "video": "https://youtube.com/xyz"})

    assert response.status_code == 422
    repository.create.assert_not_called()
