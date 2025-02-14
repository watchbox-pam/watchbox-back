import json

import requests
from psycopg import sql
from psycopg.connection import Connection


def fill_languages(base_url: str, headers, conn: Connection):
    endpoint: str = "configuration/languages"

    url = base_url + endpoint

    response = requests.get(url, headers=headers)

    python_dict = json.loads(response.text)

    query = sql.SQL("INSERT INTO public.language (iso, english_name, name) VALUES {}").format(
        sql.SQL(",").join(sql.SQL("(%s, %s, %s)") for _ in python_dict)
    )

    values = []
    for row in python_dict:
        for item in (row["iso_639_1"], row["english_name"], row["name"]):
            values.append(item)

    cur = conn.cursor()
    cur.execute(query, values)
    conn.commit()
    cur.close()
