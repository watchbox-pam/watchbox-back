import datetime
from contextlib import contextmanager

import pytest

import repository.admin_user_repository as admin_user_repository_module
import repository.user_repository as user_repository_module
from database.models import Country as DBCountry
from domain.models.userSignup import UserSignup
from repository.admin_user_repository import AdminUserRepository
from repository.user_repository import UserRepository

FRANCE = DBCountry(iso="FR", name="France", exists=True, user=[])


class FakeSession:
    """Session minimale : renvoie le pays demandé et retient les objets ajoutés (sans base de données)."""

    def __init__(self):
        self.added = []

    def get(self, model, key):
        return FRANCE if model is DBCountry and key == "FR" else None

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        pass

    def refresh(self, obj):
        pass


@pytest.fixture
def fake_session(monkeypatch):
    session = FakeSession()

    @contextmanager
    def session_local():
        yield session

    monkeypatch.setattr(user_repository_module, "SessionLocal", session_local)
    monkeypatch.setattr(admin_user_repository_module, "SessionLocal", session_local)
    return session


def signup(country):
    return UserSignup(id="11111111-1111-1111-1111-111111111111", username="arno", email="arno@mail.com",
                      password="x" * 64, salt="s" * 32, country=country, birthdate=datetime.date(1990, 1, 1))


def test_signup_keeps_the_country(fake_session):
    # Avec country_=None, SQLAlchemy vidait la colonne country à l'enregistrement
    assert UserRepository().create_user(signup("FR"), "reset", "123456", "verif") is True

    user = fake_session.added[0]
    assert user.country == "FR"
    assert user.country_ is FRANCE


def test_signup_with_unknown_country_does_not_crash(fake_session):
    assert UserRepository().create_user(signup("ZZ"), "reset", "123456", "verif") is True
    assert fake_session.added[0].country_ is None


def test_admin_created_user_keeps_the_country(fake_session):
    AdminUserRepository().create_with_playlist({
        "username": "admin-cree", "email": "a@mail.com", "password": "h", "salt": "s" * 32,
        "birthdate": datetime.date(2000, 1, 1), "is_private": False, "history_private": False,
        "adult_content": False, "is_verified": True, "country": "FR",
        "profile_picture_path": None, "banner_path": None,
    })

    user = fake_session.added[0]
    assert user.country == "FR"
    assert user.country_ is FRANCE
