import json

import requests
from psycopg import sql
from psycopg.connection import Connection


def fill_providers(base_url: str, headers, conn: Connection):
    endpoint: str = "watch/providers/movie?language=fr-FR"

    url = base_url + endpoint

    response = requests.get(url, headers=headers)

    movies_python_dict = json.loads(response.text)

    endpoint: str = "watch/providers/tv?language=fr-FR"

    url = base_url + endpoint

    response = requests.get(url, headers=headers)

    python_dict = json.loads(response.text)

    for aLis1 in movies_python_dict:
        if aLis1 not in python_dict:
            python_dict.append(aLis1)

    query = sql.SQL("INSERT INTO public.media_provider (id, name, logo, display_priority) VALUES {}").format(
        sql.SQL(",").join(sql.SQL("(%s, %s, %s, %s)") for _ in python_dict["results"])
    )

    values = []
    #print(python_dict["results"])
    for row in python_dict["results"]:
        for item in (row["provider_id"], row["provider_name"], row["logo_path"], row["display_priority"]):
            values.append(item)

    cur = conn.cursor()
    cur.execute(query, values)
    conn.commit()
    cur.close()
