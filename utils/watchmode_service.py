import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def call_watchmode_api(endpoint: str, params: dict = {}):
    base_url = os.getenv("WATCHMODE_BASE")
    api_key = os.getenv("WATCHMODE_API_KEY")

    if not base_url or not api_key:
        return {"error": "Missing WATCHMODE_BASE or WATCHMODE_API_KEY"}
    
    params["apiKey"] = api_key
    url = base_url + endpoint

    try:
        response = requests.get(url, params=params)
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
