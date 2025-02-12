import json

import requests
from psycopg import sql
from psycopg.connection import Connection


def fill_countries(base_url: str, headers, conn: Connection):
    endpoint: str = "configuration/countries?language=fr-FR"

    url = base_url + endpoint

    response = requests.get(url, headers=headers)

    python_dict = json.loads(response.text)

    query = sql.SQL("INSERT INTO public.country (iso, name) VALUES {}").format(
        sql.SQL(",").join(sql.SQL("(%s, %s)") for _ in python_dict)
    )

    values = []
    for row in python_dict:
        for item in (row["iso_3166_1"], row["native_name"]):
            values.append(item)

    cur = conn.cursor()
    cur.execute(query, values)
    conn.commit()
    cur.close()
