from typing import List, Dict, Any

from utils.tmdb_service import call_tmdb_api


class ProviderRepository:
    def get_providers(self) -> List[Dict[str, Any]]:
        """
        Get all available streaming providers from TMDB
        """
        endpoint = "/watch/providers/movie?language=fr-FR&watch_region=FR"
        result = call_tmdb_api(endpoint)

        providers = []
        if "results" in result:
            for item in result["results"]:
                providers.append({
                    "id": item.get("provider_id"),
                    "name": item.get("provider_name", ""),
                    "logo_path": item.get("logo_path"),
                })

        return providers

    def get_movie_providers(self, movie_id: int) -> List[Dict[str, Any]]:
        """
        Get streaming providers for a specific movie
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
                        "logo_path": provider.get("logo_path"),
                        "type": self._get_provider_type(provider.get("provider_id"), fr_providers)
                    })

        return providers

    def _get_provider_type(self, provider_id: int, fr_providers: Dict[str, Any]) -> str:
        """
        Helper method to determine the provider type (flatrate, rent, buy)
        """
        if "flatrate" in fr_providers and any(p["provider_id"] == provider_id for p in fr_providers["flatrate"]):
            return "flatrate"
        elif "rent" in fr_providers and any(p["provider_id"] == provider_id for p in fr_providers["rent"]):
            return "rent"
        elif "buy" in fr_providers and any(p["provider_id"] == provider_id for p in fr_providers["buy"]):
            return "buy"
        else:
            return "unknown"