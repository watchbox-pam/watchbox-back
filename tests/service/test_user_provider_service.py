import datetime

import pytest

from domain.models.providerErrors import InvalidProviderError, ProviderCatalogUnavailableError
from service.user_provider_service import UserProviderService

CATALOG = [
    {"id": 8, "name": "Netflix", "logo_path": "/netflix.jpg", "display_priority": 1},
    {"id": 337, "name": "Disney Plus", "logo_path": "/disney.jpg", "display_priority": 2},
    {"id": 119, "name": "Amazon Prime Video", "logo_path": "/prime.jpg", "display_priority": 3},
]


class FakeProviderRepository:
    def __init__(self, catalog=None):
        self.catalog = CATALOG if catalog is None else catalog
        self.calls = 0

    def get_providers(self):
        self.calls += 1
        return self.catalog


class FakeUserProviderRepository:
    def __init__(self):
        self.selection = {}
        self.onboarding = {}

    def get_user_providers(self, user_id):
        return [{"id": p["id"], "name": p["name"], "logo_path": p["logo_path"]} for p in self.selection.get(user_id, [])]

    def replace_user_providers(self, user_id, providers):
        self.selection[user_id] = list(providers)

    def get_onboarding_completed_at(self, user_id):
        return self.onboarding.get(user_id)

    def complete_onboarding(self, user_id):
        self.onboarding.setdefault(user_id, datetime.datetime(2026, 11, 24, 21, 0))
        return self.onboarding[user_id]


@pytest.fixture
def repo():
    return FakeUserProviderRepository()


def test_set_providers_replaces_selection_and_removes_duplicates(repo):
    service = UserProviderService(repo, FakeProviderRepository())

    service.set_user_providers("u1", [8, 337])
    result = service.set_user_providers("u1", [119, 8, 119])

    assert [p["id"] for p in result] == [119, 8]
    assert repo.selection["u1"][0]["display_priority"] == 3  # infos du catalogue transmises au repository


def test_set_providers_rejects_unknown_ids_without_touching_selection(repo):
    service = UserProviderService(repo, FakeProviderRepository())
    service.set_user_providers("u1", [8])

    with pytest.raises(InvalidProviderError) as error:
        service.set_user_providers("u1", [8, 999, 1000])

    assert error.value.unknown_ids == [999, 1000]
    assert [p["id"] for p in repo.selection["u1"]] == [8]


def test_set_providers_with_empty_list_clears_without_calling_tmdb(repo):
    providers = FakeProviderRepository()
    service = UserProviderService(repo, providers)
    service.set_user_providers("u1", [8])
    providers.calls = 0

    assert service.set_user_providers("u1", []) == []
    assert providers.calls == 0


def test_set_providers_when_catalog_unavailable(repo):
    service = UserProviderService(repo, FakeProviderRepository(catalog=[]))

    with pytest.raises(ProviderCatalogUnavailableError):
        service.set_user_providers("u1", [8])
    assert "u1" not in repo.selection


def test_complete_onboarding_keeps_first_date(repo):
    service = UserProviderService(repo, FakeProviderRepository())

    assert service.get_onboarding_completed_at("u1") is None
    first = service.complete_onboarding("u1")
    repo.onboarding["u1"] = first
    assert service.complete_onboarding("u1") == first
