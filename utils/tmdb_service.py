import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def call_tmdb_api(endpoint: str):
    base_url = os.getenv("TMDB_BASE_URL")
    api_key = os.getenv("TMDB_API_KEY")

    if not base_url or not api_key:
        return {"error": "Missing TMDB_BASE_URL or TMDB_API_KEY"}

    url = base_url + endpoint
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(url, headers=headers)
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
