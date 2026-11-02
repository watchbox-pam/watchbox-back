import json
import logging
import os
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def call_tmdb_api(endpoint: str):
    base_url = os.getenv("TMDB_BASE_URL")
    api_key = os.getenv("TMDB_API_KEY")

    if not base_url or not api_key:
        logger.error("TMDB_BASE_URL ou TMDB_API_KEY manquant")
        return {"error": "Missing TMDB_BASE_URL or TMDB_API_KEY"}

    url = base_url + endpoint
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        try:
            return response.json()
        except ValueError:
            logger.error("Réponse TMDB non JSON (%s) pour %s", response.status_code, endpoint)
            return {"error": "Invalid JSON response"}
    except requests.exceptions.RequestException as e:
        logger.error("Appel TMDB échoué pour %s : %s", endpoint, e)
        return {"error": str(e)}
