from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.filmFestivals import FilmFestival

class IFilmFestivalRepository(ABC):
    @abstractmethod
    async def get_all_festivals(self) -> List[FilmFestival]:
        """Récupère tous les festivals"""
        pass

    @abstractmethod
    async def get_festivals_by_year(self, year: int) -> List[FilmFestival]:
        """Récupère les festivals pour une année donnée"""
        pass

    @abstractmethod
    async def get_festival_by_id(self, festival_id: str) -> Optional[FilmFestival]:
        """Récupère un festival par son ID"""
        pass