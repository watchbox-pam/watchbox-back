import json

import requests
from psycopg import sql
from psycopg.connection import Connection


def fill_persons(base_url: str, headers, conn: Connection):
    endpoint: str = "person/83002?language=fr-FR"

    url = base_url + endpoint

    response = requests.get(url, headers=headers)

    results = json.loads(response.text)
    print(results)

    query = "INSERT INTO public.person (id, adult, also_known_as, biography, birthday, deathday, gender, homepage, imdb_id, known_for_department, name, place_of_birth, profile_path) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    print(query)

    values = []
    for item in (results["id"], results["adult"], results["also_known_as"], results["biography"], results["birthday"], results["deathday"], results["gender"], results["homepage"], results["imdb_id"], results["known_for_department"], results["name"], results["place_of_birth"], results["profile_path"]):
        values.append(item)

    cur = conn.cursor()
    cur.execute(query, values)
    conn.commit()
    cur.close()
