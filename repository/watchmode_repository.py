import os
import httpx
from dotenv import load_dotenv

load_dotenv()

WATCHMODE_API_KEY = os.getenv("WATCHMODE_API_KEY")
WATCHMODE_BASE = os.getenv("WATCHMODE_BASE")

def get_streaming_links(tmdb_id: int) -> dict:
    try:
        with httpx.Client() as client:
            search_res = client.get(
                f"{WATCHMODE_BASE}/search/",
                params={
                    "apiKey": WATCHMODE_API_KEY,
                    "search_field": "tmdb_movie_id",
                    "search_value": tmdb_id
                },
                timeout=5.0
            )
            results = search_res.json().get("title_results", [])
            if not results:
                print(f"[WATCHMODE] Aucun résultat pour tmdb_id={tmdb_id}")
                return {}

            watchmode_id = results[0]["id"]

            sources_res = client.get(
                f"{WATCHMODE_BASE}/title/{watchmode_id}/sources/",
                params={
                    "apiKey": WATCHMODE_API_KEY,
                    "regions": "FR"
                },
                timeout=5.0
            )
            sources = sources_res.json()
            print(f"[WATCHMODE] sources={sources[:2]}")

            result = {}
            for source in sources:
                name = source.get("name", "").lower().replace(" ", "").replace("+", "plus")
                url = source.get("web_url")
                if name and url and name not in result:
                    result[name] = url
            return result

    except Exception as e:
        print(f"[WATCHMODE] Error: {e}")
        return {}