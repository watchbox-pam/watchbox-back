import random

from service.onboarding_movie_service import OnboardingMovieService

ACTION, DRAME, COMEDIE, HORREUR, ANIMATION = 28, 18, 35, 27, 16


def movie(movie_id, genres, available=False):
    return {"id": movie_id, "title": f"Film {movie_id}", "poster_path": f"/{movie_id}.jpg",
            "popularity": 100.0, "genre_ids": genres, "available": available}


class FakeOnboardingRepository:
    def __init__(self, candidates):
        self.candidates = candidates
        self.calls = []

    def get_candidates(self, user_id, include_adult, provider_ids, pool_size):
        self.calls.append((user_id, include_adult, provider_ids, pool_size))
        return self.candidates


class FakeUserProviderRepository:
    def __init__(self, provider_ids):
        self.provider_ids = provider_ids

    def get_user_providers(self, user_id):
        return [{"id": i, "name": str(i), "logo_path": None} for i in self.provider_ids]


def make_service(candidates, provider_ids=()):
    repo = FakeOnboardingRepository(candidates)
    return OnboardingMovieService(repo, FakeUserProviderRepository(list(provider_ids)), rng=random.Random(42)), repo


def test_passes_user_providers_and_adult_flag_to_repository():
    service, repo = make_service([movie(1, [ACTION])], provider_ids=[8, 337])

    result = service.get_onboarding_movies("u1", 15, include_adult=False)

    assert repo.calls == [("u1", False, [8, 337], OnboardingMovieService.POOL_SIZE)]
    assert [m.id for m in result] == [1]
    assert result[0].poster_path == "/1.jpg"


def test_limits_each_genre_when_enough_variety():
    candidates = [movie(i, [ACTION]) for i in range(1, 11)] + \
                 [movie(i, [genre]) for i, genre in zip(range(11, 21), [DRAME, COMEDIE, HORREUR, ANIMATION] * 3)]
    service, _ = make_service(candidates)

    picked = service.select_movies(candidates, 15)

    assert len(picked) == 15
    assert len({m["id"] for m in picked}) == 15
    action_count = sum(1 for m in picked if ACTION in m["genre_ids"])
    # 1re passe : 3 films d'action max + les 10 autres = 13, puis 2 de complément
    assert action_count == OnboardingMovieService.MAX_PER_GENRE + 2


def test_fills_up_when_not_enough_variety():
    candidates = [movie(i, [ACTION]) for i in range(1, 21)]
    service, _ = make_service(candidates)

    picked = service.select_movies(candidates, 15)

    assert len(picked) == 15  # pas de trou même si tout est du même genre


def test_prefers_movies_available_on_user_platforms():
    available = [movie(i, [g], available=True) for i, g in zip(range(1, 6), [ACTION, DRAME, COMEDIE, HORREUR, ANIMATION])]
    others = [movie(i, [g]) for i, g in zip(range(100, 120), [ACTION, DRAME, COMEDIE, HORREUR, ANIMATION] * 4)]
    service, _ = make_service(available + others)

    picked = service.select_movies(available + others, 8)

    assert {m["id"] for m in available} <= {m["id"] for m in picked}


def test_returns_what_exists_when_catalog_is_small():
    service, _ = make_service([movie(1, [ACTION]), movie(2, [])])

    assert len(service.get_onboarding_movies("u1", 15, include_adult=True)) == 2
