import json

import requests
from psycopg import sql
from psycopg.connection import Connection


def fill_genres(base_url: str, headers, conn: Connection):
    cur = conn.cursor()
    endpoint: str = "genre/movie/list?language=fr"

    url = base_url + endpoint

    response = requests.get(url, headers=headers)

    python_dict = json.loads(response.text)
    genre_list = python_dict["genres"]

    query_movies = sql.SQL("INSERT INTO public.movie_genre (id, name) VALUES {}").format(
        sql.SQL(",").join(sql.SQL("(%s, %s)") for _ in genre_list)
    )

    values_movies = []
    for row in genre_list:
        for item in (row["id"], row["name"]):
            values_movies.append(item)

    cur.execute(query_movies, values_movies)

    endpoint: str = "genre/tv/list?language=fr"

    url = base_url + endpoint

    response = requests.get(url, headers=headers)

    python_dict = json.loads(response.text)
    genre_list = python_dict["genres"]

    query_tv = sql.SQL("INSERT INTO public.tv_genre (id, name) VALUES {}").format(
        sql.SQL(",").join(sql.SQL("(%s, %s)") for _ in genre_list)
    )

    values_tv = []
    for row in genre_list:
        for item in (row["id"], row["name"]):
            values_tv.append(item)

    cur.execute(query_tv, values_tv)
    conn.commit()
    cur.close()
