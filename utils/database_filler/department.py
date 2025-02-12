import json

import requests
from psycopg import sql
from psycopg.connection import Connection


def fill_departments(base_url: str, headers, conn: Connection):
    cur = conn.cursor()
    endpoint: str = "configuration/jobs"

    url = base_url + endpoint

    response = requests.get(url, headers=headers)

    python_dict = json.loads(response.text)


    for row in python_dict:
        query_departments = "INSERT INTO public.department (name) VALUES (%s) RETURNING id"
        cur.execute(query_departments, (row["department"],))

        inserted_id = cur.fetchone()[0]

        query_jobs = sql.SQL("INSERT INTO public.job (name, department_id) VALUES {}").format(
            sql.SQL(",").join(sql.SQL("(%s, %s)") for _ in row["jobs"])
        )

        values_jobs = []
        for item in row["jobs"]:
            values_jobs.append(item)
            values_jobs.append(inserted_id)

        cur.execute(query_jobs, values_jobs)

    conn.commit()
    cur.close()
