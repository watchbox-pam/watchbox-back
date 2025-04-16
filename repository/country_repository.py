import db_config
from domain.interfaces.repositories.i_country_repository import ICountryRepository
from domain.models.country import Country


class CountryRepository(ICountryRepository):
    def find_all_countries(self) -> list[Country]:

        countries: list[Country] = []

        with db_config.connect_to_db() as conn:
            with conn.cursor() as cur:
                query = "SELECT * FROM public.country;"

                cur.execute(query)
                result = cur.fetchall()
                for res in result:
                    countries.append(Country(iso=res[0], name=res[1]))

        return countries