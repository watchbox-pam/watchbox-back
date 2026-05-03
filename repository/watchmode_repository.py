import os
from utils.watchmode_service import call_watchmode_api

def get_streaming_links(tmdb_id: int) -> dict:
  try:
      search_data = call_watchmode_api("/search/",{
        "search_field": "tmdb_movie_id",
        "search_value": tmdb_id
      })
      results = search_data.get("title_results", [])
      if not results:
        print(f"[WATCHMODE] Aucun résultat pour tmdb_id={tmdb_id}")
        return {}

      watchmode_id = results[0]["id"]

      sources = call_watchmode_api(
        f"/title/{watchmode_id}/sources/",{
            "regions": "FR"
        })

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