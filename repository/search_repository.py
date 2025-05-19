from typing import List, Dict, Any

from domain.interfaces.repositories.i_search_repository import ISearchRepository
from utils.tmdb_service import call_tmdb_api


class SearchRepository(ISearchRepository):
    def search_all(self, search_term: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for movies, TV shows, and people matching the search term
        """
        endpoint = f"/search/multi?query={search_term}&language=fr-FR&page=1&include_adult=false"
        result = call_tmdb_api(endpoint)

        # Organize results by category
        movies = []
        people = []
        tv = []

        if "results" in result:
            for item in result["results"]:
                media_type = item.get("media_type")
                if media_type == "movie":
                    movies.append({
                        "id": item.get("id"),
                        "title": item.get("title", ""),
                        "poster_path": item.get("poster_path"),
                        "release_date": item.get("release_date", ""),
                        "media_type": "movie"
                    })
                elif media_type == "person":
                    people.append({
                        "id": item.get("id"),
                        "name": item.get("name", ""),
                        "profile_path": item.get("profile_path"),
                        "known_for_department": item.get("known_for_department", ""),
                        "media_type": "person"
                    })
                elif media_type == "tv":
                    tv.append({
                        "id": item.get("id"),
                        "title": item.get("name", ""),
                        "poster_path": item.get("poster_path"),
                        "first_air_date": item.get("first_air_date", ""),
                        "media_type": "tv"
                    })

        return {
            "movies": movies,
            "people": people,
            "tv": tv
        }

    def search_movies(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search only for movies matching the search term
        """
        endpoint = f"/search/movie?query={search_term}&language=fr-FR&page=1&include_adult=false"
        result = call_tmdb_api(endpoint)

        movies = []
        if "results" in result:
            for item in result["results"]:
                movies.append({
                    "id": item.get("id"),
                    "title": item.get("title", ""),
                    "poster_path": item.get("poster_path"),
                    "release_date": item.get("release_date", ""),
                    "overview": item.get("overview", ""),
                    "vote_average": item.get("vote_average", 0),
                    "media_type": "movie"
                })

        return movies

    def search_actors(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search only for actors/people matching the search term
        """
        endpoint = f"/search/person?query={search_term}&language=fr-FR&page=1&include_adult=false"
        result = call_tmdb_api(endpoint)

        people = []
        if "results" in result:
            for item in result["results"]:
                person = {
                    "id": item.get("id"),
                    "name": item.get("name", ""),
                    "profile_path": item.get("profile_path"),
                    "known_for_department": item.get("known_for_department", ""),
                    "media_type": "person"
                }

                # Include known_for movies/shows
                known_for = []
                for known_item in item.get("known_for", []):
                    media_title = known_item.get("title") if known_item.get(
                        "media_type") == "movie" else known_item.get("name")
                    known_for.append({
                        "id": known_item.get("id"),
                        "title": media_title,
                        "media_type": known_item.get("media_type")
                    })

                person["known_for"] = known_for
                people.append(person)

        return people