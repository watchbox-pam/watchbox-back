from typing import List, Dict, Any, Optional

from domain.interfaces.repositories.i_search_repository import ISearchRepository
from utils.tmdb_service import call_tmdb_api


class SearchRepository(ISearchRepository):

    def search_all(self, search_term: str, providers: Optional[List[int]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for movies, TV shows, and people matching the search term and optional provider filters
        """
        movies = self.search_movies(search_term, providers)
        people = self.search_actors(search_term)

        return {
            "movies": movies,
            "people": people,
            "tv": []
        }

    def search_movies(self, search_term: str, providers: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        Search only for movies matching the search term and optional provider filters
        """
        endpoint = f"/search/movie?query={search_term}&language=fr-FR&page=1&include_adult=false"
        result = call_tmdb_api(endpoint)

        movies = []
        if "results" in result:
            for item in result["results"]:

                if not item.get("poster_path"):
                    continue
                if not item.get("overview", "").strip():
                    continue

                # If providers filter is active, check if the movie is available on selected providers
                if providers:
                    movie_providers = self._get_movie_providers(item.get("id"))
                    provider_ids = [p.get("id") for p in movie_providers]

                    # If there's no intersection between requested providers and movie providers, skip this movie
                    if not set(providers).intersection(set(provider_ids)):
                        continue

                movies.append({
                    "id": item.get("id"),
                    "title": item.get("title", ""),
                    "poster_path": item.get("poster_path"),
                    "release_date": item.get("release_date", ""),
                    "overview": item.get("overview", ""),
                    "vote_average": item.get("vote_average", 0),
                    "media_type": "movie",
                    "original_title": item.get("original_title", ""),
                    "popularity": item.get("popularity", 0),
                })

        movies.sort(key=lambda x: x['popularity'], reverse=True)

        return movies

    def search_actors(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search only for actors/people matching the search term
        """
        people = []
        seen_ids = set()

        for page in range(1, 6):
            endpoint = f"/search/person?query={search_term}&language=fr-FR&page={page}&include_adult=false"
            result = call_tmdb_api(endpoint)

            if "results" not in result or not result["results"]:
                break

            for item in result["results"]:
                name = item.get("name", "")
                profile_path = item.get("profile_path")

                if not profile_path:
                    continue
                if len(name.strip().split()) < 2:
                    continue

                if item.get("id") in seen_ids:
                    continue
                seen_ids.add(item.get("id"))

                person = {
                    "id": item.get("id"),
                    "name": item.get("name", ""),
                    "profile_path": item.get("profile_path"),
                    "known_for_department": item.get("known_for_department", ""),
                    "media_type": "person",
                    "popularity": item.get("popularity", 0),
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

            total_pages = result.get("total_pages", 1)
            if page >= total_pages or len(people) >= 20:
                break
        
        people.sort(key=lambda x: x['popularity'], reverse=True)
        return people
    
    def search_suggestions(self, search_term: str, providers: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        Search for movies, TV shows, and people matching the search term and optional provider filters
        Returns only top 5 results per category without overview to be used as search suggestions
        """
        endpoint = f"/search/multi?query={search_term}&language=fr-FR&page=1&include_adult=false"
        results = call_tmdb_api(endpoint)

        suggestions = []

        if "results" in results:
            for item in results["results"]:
                media_type = item.get("media_type")
                if media_type not in ["movie", "person"]:
                    continue

                if media_type == "movie":

                    if not item.get("poster_path"):
                        continue

                    if providers:
                        movie_providers = self._get_movie_providers(item.get("id"))
                        provider_ids = [p.get("id") for p in movie_providers]
                        if not set(providers).intersection(set(provider_ids)):
                            continue

                    suggestions.append({
                        "id": item.get("id"),
                        "title": item.get("title", ""),
                        "original_title": item.get("original_title", ""),
                        "poster_path": item.get("poster_path"),
                        "media_type": "movie",
                        "popularity": item.get("popularity", 0),
                        "release_date": item.get("release_date", "")
                    })
                elif media_type == "person":

                    if not item.get("profile_path"):
                        continue

                    if len(item.get("name", "").strip().split()) < 2:
                        continue

                    suggestions.append({
                        "id": item.get("id"),
                        "name": item.get("name", ""),
                        "profile_path": item.get("profile_path"),
                        "media_type": "person",
                        "popularity": item.get("popularity", 0),
                        "known_for_department": item.get("known_for_department", ""),
                    })

        suggestions.sort(key=lambda x: x['popularity'], reverse=True)

        seen_titles = set()
        unique_suggestions = []
        for item in suggestions:
            title = (item.get("title") or item.get("name", ""))
            if title not in seen_titles:
                seen_titles.add(title)
                unique_suggestions.append(item)
            if len(unique_suggestions) == 5:
                break

        return unique_suggestions

    def _get_movie_providers(self, movie_id: int) -> List[Dict[str, Any]]:
        """
        Helper method to get providers for a specific movie
        """
        endpoint = f"/movie/{movie_id}/watch/providers"
        result = call_tmdb_api(endpoint)

        providers = []
        if "results" in result and "FR" in result["results"]:
            # Get the French providers
            fr_providers = result["results"]["FR"]

            # Combine all types of providers (flatrate, rent, buy)
            all_providers = []
            if "flatrate" in fr_providers:
                all_providers.extend(fr_providers["flatrate"])
            if "rent" in fr_providers:
                all_providers.extend(fr_providers["rent"])
            if "buy" in fr_providers:
                all_providers.extend(fr_providers["buy"])

            # Remove duplicates by provider_id
            seen_ids = set()
            for provider in all_providers:
                if provider["provider_id"] not in seen_ids:
                    seen_ids.add(provider["provider_id"])
                    providers.append({
                        "id": provider.get("provider_id"),
                        "name": provider.get("provider_name", ""),
                        "logo_path": provider.get("logo_path")
                    })

        return providers