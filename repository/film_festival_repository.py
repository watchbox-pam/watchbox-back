from typing import List, Optional
from domain.interfaces.repositories.i_film_festival_repository import IFilmFestivalRepository
from domain.models.filmFestivals import FilmFestival

class FilmFestivalRepository(IFilmFestivalRepository):
    def __init__(self):
        self.festivals = [
            FilmFestival(
                id="sundance-2025",
                name="Festival de Sundance",
                location="Park City, Utah, USA",
                start_date="23-01-2025",
                end_date="02-02-2025",
                description="Le plus grand festival de cinéma indépendant américain",
                website="https://www.sundance.org"
            ),
            FilmFestival(
                id="berlin-2025",
                name="Berlinale",
                location="Berlin, Allemagne",
                start_date="13-02-2025",
                end_date="23-02-2025",
                description="Festival International du Film de Berlin",
                website="https://www.berlinale.de"
            ),
            FilmFestival(
                id="cannes-2025",
                name="Festival de Cannes",
                location="Cannes, France",
                start_date="13-05-2025",
                end_date="24-05-2025",
                description="Le plus prestigieux festival de cinéma au monde",
                website="https://www.festival-cannes.com"
            ),
            FilmFestival(
                id="venice-2025",
                name="Mostra de Venise",
                location="Venise, Italie",
                start_date="27-08-2025",
                end_date="06-09-2025",
                description="Le plus ancien festival de cinéma au monde",
                website="https://www.labiennale.org"
            ),
            FilmFestival(
                id="toronto-2025",
                name="TIFF",
                location="Toronto, Canada",
                start_date="04-09-2025",
                end_date="14-09-2025",
                description="Festival International du Film de Toronto",
                website="https://www.tiff.net"
            ),
            FilmFestival(
                id="deauville-2025",
                name="Festival de Deauville",
                location="Deauville, France",
                start_date="05-09-2025",
                end_date="14-09-2025",
                description="Festival du Cinéma Américain de Deauville",
                website="https://www.festival-deauville.com"
            ),
            FilmFestival(
                id="annecy-2025",
                name="Festival d'Annecy",
                location="Annecy, France",
                start_date="09-06-2025",
                end_date="14-06-2025",
                description="Festival International du Film d'Animation",
                website="https://www.annecy.org"
            ),
            FilmFestival(
                id="clermont-2025",
                name="Festival de Clermont-Ferrand",
                location="Clermont-Ferrand, France",
                start_date="31-01-2025",
                end_date="08-02-2025",
                description="Festival International du Court Métrage",
                website="https://www.clermont-filmfest.org"
            ),
            FilmFestival(
                id="tribeca-2025",
                name="Tribeca Film Festival",
                location="New York, USA",
                start_date="04-06-2025",
                end_date="15-06-2025",
                description="Festival de cinéma de Tribeca",
                website="https://www.tribecafilm.com"
            ),
            FilmFestival(
                id="locarno-2025",
                name="Festival de Locarno",
                location="Locarno, Suisse",
                start_date="06-08-2025",
                end_date="16-08-2025",
                description="Festival International du Film de Locarno",
                website="https://www.locarnofestival.ch"
            ),
        ]

    async def get_all_festivals(self) -> List[FilmFestival]:
        return self.festivals

    async def get_festivals_by_year(self, year: int) -> List[FilmFestival]:
        return [
            festival for festival in self.festivals
            if int(festival.start_date.split("-")[2]) == year
        ]

    async def get_festival_by_id(self, festival_id: str) -> Optional[FilmFestival]:
        return next(
            (festival for festival in self.festivals if festival.id == festival_id),
            None
        )