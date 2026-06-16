from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List

from domain.interfaces.repositories.i_movie_repository import IMovieRepository
from domain.interfaces.services.i_movie_service import IMovieService
from domain.models.movie import Movie, MovieDetail, PopularMovieList
from domain.interfaces.repositories.i_release_dates_repository import IReleaseDatesRepository
from domain.interfaces.repositories.i_credits_repository import ICreditsRepository
from domain.interfaces.repositories.i_videos_repository import IVideosRepository
from domain.interfaces.repositories.i_watch_providers_repository import IWatchProvidersRepository
from domain.models.movie_list_item import MovieListItem
from repository.watchmode_repository import get_streaming_links

PROVIDER_FALLBACK_URLS = {
    337: "https://www.disneyplus.com/fr-fr",
    8:   "https://www.netflix.com",
    119: "https://www.primevideo.com",
    10:  "https://www.primevideo.com",
    2:   "https://tv.apple.com/fr",
    3:   "https://play.google.com/store/movies",
    192: "https://www.youtube.com",
    35:  "https://www.rakuten.tv/fr",
    61:  "https://video.orange.fr",
    381: "https://www.canalplus.com",
    384: "https://www.canalplus.com",
}
class MovieService(IMovieService):
    def __init__(self, repository: IMovieRepository, release_dates_repository: IReleaseDatesRepository, credits_repository: ICreditsRepository, videos_repository: IVideosRepository, watch_providers_repository: IWatchProvidersRepository):
        self.repository = repository
        self.release_dates_repository = release_dates_repository
        self.credits_repository = credits_repository
        self.videos_repository = videos_repository
        self.watch_providers_repository = watch_providers_repository

    def find_by_id(self, movie_id: int, include_adult: bool) -> Optional[MovieDetail]:
        with ThreadPoolExecutor() as executor:
            f_movie          = executor.submit(self.repository.find_by_id, movie_id, include_adult)
            f_release_dates  = executor.submit(self.release_dates_repository.find_by_id, movie_id)
            f_credits        = executor.submit(self.credits_repository.find_by_id, movie_id, include_adult)
            f_videos         = executor.submit(self.videos_repository.find_by_id, movie_id)
            f_watch_providers = executor.submit(self.watch_providers_repository.find_by_id, movie_id)
            f_deeplinks      = executor.submit(get_streaming_links, movie_id)

        movie          = f_movie.result()
        release_dates  = f_release_dates.result()
        credits        = f_credits.result()
        videos         = f_videos.result()
        watch_providers = f_watch_providers.result()
        deeplinks      = f_deeplinks.result()

        fr_data = watch_providers.results.get("FR", {})
        providers_link = fr_data.get("link", None)

        seen = set()
        france_providers = []
        for p in [*fr_data.get("flatrate", []), *fr_data.get("rent", []), *fr_data.get("buy", [])]:
            if p["provider_id"] not in seen:
                seen.add(p["provider_id"])
                technical = p.get("provider_name", "").lower().replace(" ", "").replace("+", "plus")
                web_url = deeplinks.get(technical) or next(
                    (v for k, v in deeplinks.items() if k.lower() in technical or technical in k.lower()),
                    None
                )
                if not web_url:
                    web_url = PROVIDER_FALLBACK_URLS.get(p["provider_id"], providers_link)

                france_providers.append({
                    **p,
                    "deeplink_android": web_url,
                    "deeplink_ios": web_url,
                    "web_url": web_url
                })

        video = next((v for v in videos.results if v.get("site") == "YouTube" and v.get("type") == "Trailer"), None)
        casting = credits.cast if credits else None
        crew = credits.crew if credits else None
        director = next((c for c in crew if c.get("known_for_department") == "Directing"), None)
        composer = next((c for c in crew if c.get("known_for_department") == "Sound"), None)

        france_release_date = None
        for result in release_dates.results:
            if result.get("iso_3166_1") == "FR":
                for release in result.get("release_dates", []):
                    if release.get("type") == 3:
                        france_release_date = release
                        break
                if france_release_date:
                    break

        return {
            "id": movie.id,
            "adult": movie.adult,
            "backdrop_path": movie.backdrop_path,
            "budget": movie.budget,
            "genres": movie.genres,
            "original_language": movie.original_language,
            "original_title": movie.original_title,
            "overview": movie.overview,
            "poster_path": movie.poster_path,
            "release_date": movie.release_date,
            "revenue": movie.revenue,
            "runtime": movie.runtime,
            "status": movie.status,
            "title": movie.title,
            "video": movie.video,
            "age_restriction": france_release_date.get("certification") if france_release_date else None,
            "casting": casting,
            "director": director,
            "composer": composer,
            "video_key": video["key"] if video else None,
            "providers": france_providers,
            "providers_link": providers_link
        }

    def search(self, search_term: str, include_adult: bool) -> Optional[list[Movie]]:
        return self.repository.search(search_term, include_adult)

    def find_by_time_window(self, time_window: str, page: int, include_adult: bool) -> Optional[Movie]:
        return self.repository.find_by_time_window(time_window, page, include_adult)

    def find_by_genre(self, genre: str, include_adult: bool) -> Optional[PopularMovieList]:
        return self.repository.find_by_genre(genre, include_adult)

    def get_random_movies(self, count: int = 50, include_adult: bool = False) -> Optional[List[MovieListItem]]:
        movies = self.repository.get_random_movies(count, include_adult)
        if not movies or len(movies) == 0:
            return None
        return movies