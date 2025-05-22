from typing import Optional, List

from domain.interfaces.repositories.i_movie_repository import IMovieRepository
from domain.interfaces.services.i_movie_service import IMovieService
from domain.models.movie import Movie, MovieDetail, PopularMovieList
from domain.interfaces.repositories.i_release_dates_repository import IReleaseDatesRepository
from domain.interfaces.repositories.i_credits_repository import ICreditsRepository
from domain.interfaces.repositories.i_videos_repository import IVideosRepository
from domain.interfaces.repositories.i_watch_providers_repository import IWatchProvidersRepository
from domain.models.movie_list_item import MovieListItem


class MovieService(IMovieService):
    def __init__(self, repository: IMovieRepository, release_dates_repository: IReleaseDatesRepository, credits_repository: ICreditsRepository, videos_repository: IVideosRepository, watch_providers_repository: IWatchProvidersRepository):
        self.repository = repository
        self.release_dates_repository = release_dates_repository
        self.credits_repository = credits_repository
        self.videos_repository = videos_repository
        self.watch_providers_repository = watch_providers_repository

    def find_by_id(self, movie_id: int) -> Optional[MovieDetail]:
        movie = self.repository.find_by_id(movie_id)
        release_dates = self.release_dates_repository.find_by_id(movie_id)
        credits = self.credits_repository.find_by_id(movie_id)
        videos = self.videos_repository.find_by_id(movie_id)
        watch_providers = self.watch_providers_repository.find_by_id(movie_id)

        france_providers = watch_providers.results.get("FR", {}).get("flatrate", [])

        video = next((v for v in videos.results if v.get("site") == "YouTube" and v.get("type") == "Trailer"), None)

        casting = credits.cast if credits else None
        crew = credits.crew if credits else None

        director = next((c for c in crew if (c.get("known_for_department") == "Directing")), None)
        composer = next((c for c in crew if (c.get("known_for_department") == "Sound")), None)

        # find the release date for France
        france_release_date = None
        for result in release_dates.results:
            if result.get("iso_3166_1") == "FR":
                for release in result.get("release_dates", []):
                    if release.get("type") == 3:
                        france_release_date = release
                        break  # Stop searching once found
                if france_release_date:
                    break  # Stop searching once found

        combined = {
            **movie.__dict__, 
            "age_restriction": france_release_date.get("certification") if france_release_date else None,
            "casting": casting,
            "director": director,
            "composer": composer,
            "video_key": video["key"] if video else None,
            "providers": france_providers
            }
        return combined

    def search(self, search_term: str) -> Optional[list[Movie]]:
        return self.repository.search(search_term)

    def find_by_time_window(self, time_window: str, page: int) -> Optional[Movie]:
        movie = self.repository.find_by_time_window(time_window, page)
        return movie

    def find_by_genre(self, genre: str) -> Optional[PopularMovieList]:
        movies = self.repository.find_by_genre(genre)
        return movies
    
    def get_random_movies(self, count: int = 50) -> Optional[List[MovieListItem]]:
        movies = self.repository.get_random_movies(count)

        if not movies or len(movies) == 0:
            return None

        return movies