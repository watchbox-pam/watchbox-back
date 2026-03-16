from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.event import Event

class IEventRepository(ABC):
    @abstractmethod
    async def get_all_events(self) -> List[Event]:
        """Récupère tous les événements"""
        pass

    @abstractmethod
    async def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Récupère un événement par son ID"""
        pass

    @abstractmethod
    async def get_events_by_date(self, date: str) -> List[Event]:
        """Récupère les événements pour une date donnée"""
        pass

    @abstractmethod
    async def create_event(self, event: Event) -> Event:
        """Crée un nouvel événement"""
        pass

    @abstractmethod
    async def update_event(self, event_id: str, event_data: dict) -> Event:
        """Met à jour un événement"""
        pass

    @abstractmethod
    async def delete_event(self, event_id: str) -> bool:
        """Supprime un événement"""
        pass
    