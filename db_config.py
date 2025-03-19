import os
from typing import Optional

import psycopg
from dotenv import load_dotenv

load_dotenv()

def connect_to_db() -> Optional[psycopg.connection.Connection]:
    conn = None
    try:
        params = {
            "host": os.getenv("DATABASE_HOST"),
            "dbname": os.getenv("DATABASE_NAME"),
            "user": os.getenv("DATABASE_USER"),
            "password": os.getenv("DATABASE_PASSWORD"),
            "port": os.getenv("DATABASE_PORT")
        }

        conn: psycopg.connection.Connection = psycopg.connect(**params)

        return conn
    except(Exception, psycopg.DatabaseError) as error:
        print(error)
