import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

def call_tmdb_api(endpoint: str):
    base_url = os.getenv("TMDB_BASE_URL")
    url = base_url + endpoint

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.getenv("TMDB_API_KEY")}"
    }

    response = requests.get(url, headers=headers)

    result = json.loads(response.text)

    return result
