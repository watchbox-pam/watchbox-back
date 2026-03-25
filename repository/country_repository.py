from domain.interfaces.repositories.i_country_repository import ICountryRepository
from domain.models.country import Country as CountryList
from database.db import SessionLocal
from database.models import Country as DBCountry

class CountryRepository(ICountryRepository):
    def find_all_countries(self) -> list[CountryList]:
        try:
            countries: list[CountryList] = []
            with SessionLocal() as session:
                result = session.query(DBCountry).filter(DBCountry.exists == True).all()

                for res in result:
                    countries.append(CountryList(iso=res.iso, name=res.name))

        except Exception as e:
            print(e)

        return countries