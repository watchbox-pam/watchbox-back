from abc import ABC, abstractmethod
from typing import List
from datetime import date
from domain.models.event import Event, EventCreate
from domain.models.filmFestivals import FilmFestival

class ICalendarService(ABC):
    @abstractmethod
    async def get_events_for_date(self, date: date) -> List[Event]:
        """Récupère les événements pour une date donnée"""
        pass

    @abstractmethod
    async def get_festivals_for_date(self, date: date) -> List[FilmFestival]:
        """Récupère les festivals pour une date donnée"""
        pass

    @abstractmethod
    async def has_events_on_date(self, date: date) -> bool:
        """Vérifie si une date a des événements"""
        pass

    @abstractmethod
    async def create_event(self, event_data: EventCreate) -> Event:
        """Crée un nouvel événement"""
        pass

    @abstractmethod
    async def delete_event(self, event_id: str) -> bool:
        """Supprime un événement"""
        pass