import datetime
import uuid
from types import SimpleNamespace

import pytest

import service.user_service as user_service_module
from domain.models.authErrors import AccountConflictError, InvalidRegistrationTokenError
from domain.models.googleRegistration import GoogleRegistration
from service.user_service import UserService


@pytest.fixture(autouse=True)
def jwt_config(monkeypatch):
    # Pas de dépendance au .env dans la CI
    monkeypatch.setenv("JWT_SECRET_KEY", "secret-de-test-suffisamment-long-pour-hs256")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setattr(user_service_module, "create_jwt_token", lambda payload: f"jwt-{payload['user_id']}")


class FakeUserRepository:
    def __init__(self):
        self.users = {}
        self.identities = {}

    def add_user(self, username, email, is_verified=True):
        user = SimpleNamespace(id=uuid.uuid4(), username=username, email=email,
                               is_verified=is_verified, password="hash", salt="s" * 32)
        self.users[str(user.id)] = user
        return user

    def get_user_by_provider_identity(self, provider, provider_user_id):
        return self.users.get(self.identities.get((provider, provider_user_id)))

    def get_user_by_email_insensitive(self, email):
        return next((u for u in self.users.values() if u.email.lower() == email.lower()), None)

    def get_user_by_username(self, username):
        return next((u for u in self.users.values() if u.username == username), None)

    def get_user_by_id(self, user_id):
        return self.users.get(str(user_id))

    def country_exists(self, iso):
        return iso == "FR"

    def create_external_user(self, user_id, username, email, birthdate, country, provider, provider_user_id, password_reset_token):
        self.users[user_id] = SimpleNamespace(id=uuid.UUID(user_id), username=username, email=email, is_verified=True,
                                              password=None, salt=None, birthdate=birthdate, country=country)
        self.identities[(provider, provider_user_id)] = user_id
        return True

    def link_identity(self, user_id, provider, provider_user_id, secure_unverified_account):
        self.identities[(provider, provider_user_id)] = user_id
        if secure_unverified_account:
            user = self.users[user_id]
            user.is_verified, user.password, user.salt = True, None, None
        return True

    def update_last_connection(self, user_id):
        pass


class FakePlaylistRepository:
    def __init__(self):
        self.created_for = []

    def create_playlist_on_register(self, user_id):
        self.created_for.append(user_id)


def make_service(**claims):
    claims = {"sub": "google-1", "email": "Arno@Gmail.com", "email_verified": True, "given_name": "Arnaud", **claims}
    repository, playlists = FakeUserRepository(), FakePlaylistRepository()
    return UserService(repository, playlists, google_token_verifier=lambda token: claims), repository, playlists


def registration(token, username="Arno", country="FR"):
    return GoogleRegistration(registration_token=token, username=username, birthdate=datetime.date(1995, 5, 20), country=country)


def test_first_google_login_asks_to_finish_registration_without_creating_anything():
    service, repository, _ = make_service()

    result = service.login_with_google("id-token")

    assert result["status"] == "registration_required"
    assert result["email"] == "arno@gmail.com"
    assert result["suggested_username"] == "Arnaud"
    assert repository.users == {}


def test_registration_creates_the_account_then_google_login_logs_in():
    service, repository, playlists = make_service()
    token = service.login_with_google("id-token")["registration_token"]

    created = service.register_with_google(registration(token))
    again = service.login_with_google("id-token")

    assert created["status"] == "logged_in" and created["username"] == "Arno"
    user = repository.users[created["user_id"]]
    assert user.password is None and user.birthdate == datetime.date(1995, 5, 20) and user.country == "FR"
    assert playlists.created_for == [created["user_id"]]
    assert again == {**created, "status": "logged_in"}


def test_registration_rejects_a_taken_username_and_an_unknown_country():
    service, repository, _ = make_service()
    repository.add_user("Arno", "autre@gmail.com")
    token = service.login_with_google("id-token")["registration_token"]

    with pytest.raises(AccountConflictError):
        service.register_with_google(registration(token))
    with pytest.raises(Exception, match="pays"):
        service.register_with_google(registration(token, username="Nouveau", country="ZZ"))


def test_registration_rejects_an_invalid_token():
    service, _, _ = make_service()

    with pytest.raises(InvalidRegistrationTokenError):
        service.register_with_google(registration("pas-un-jeton"))


def test_existing_verified_account_is_linked_and_keeps_its_password():
    service, repository, _ = make_service()
    existing = repository.add_user("arno", "arno@gmail.com", is_verified=True)

    result = service.login_with_google("id-token")

    assert result["status"] == "logged_in" and result["user_id"] == str(existing.id)
    assert existing.password == "hash"


def test_existing_unverified_account_is_linked_and_its_password_removed():
    service, repository, _ = make_service()
    existing = repository.add_user("arno", "arno@gmail.com", is_verified=False)

    service.login_with_google("id-token")

    assert existing.is_verified is True and existing.password is None


def test_unverified_google_email_is_refused():
    service, _, _ = make_service(email_verified=False)

    with pytest.raises(Exception, match="pas vérifiée"):
        service.login_with_google("id-token")
