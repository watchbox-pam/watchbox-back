import os

import psycopg
from dotenv import load_dotenv

import db_config
from utils.database_filler.department import fill_departments
from utils.database_filler.genre import fill_genres
from utils.database_filler.person import fill_persons
from utils.database_filler.provider import fill_providers

base_url = "https://api.themoviedb.org/3/"

load_dotenv()

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {os.getenv("TMDB_API_KEY")}"
}

conn: psycopg.connection.Connection = db_config.connect_to_db()

fill_persons(base_url, headers, conn)

conn.close()
