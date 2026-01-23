from typing import List, Optional
from domain.interfaces.repositories.i_event_repository import IEventRepository
from domain.models.event import Event

class EventRepository(IEventRepository):
    def __init__(self):
        # En mémoire pour l'instant - tu pourras le remplacer par PostgreSQL
        self.events: List[Event] = []

    async def get_all_events(self) -> List[Event]:
        return self.events

    async def get_event_by_id(self, event_id: str) -> Optional[Event]:
        return next((event for event in self.events if event.id == event_id), None)

    async def get_events_by_date(self, date: str) -> List[Event]:
        return [event for event in self.events if event.date == date]

    async def create_event(self, event: Event) -> Event:
        self.events.append(event)
        return event

    async def update_event(self, event_id: str, event_data: dict) -> Event:
        event = await self.get_event_by_id(event_id)
        if not event:
            raise ValueError(f"Event with id {event_id} not found")
        
        # Met à jour les champs
        for key, value in event_data.items():
            if hasattr(event, key):
                setattr(event, key, value)
        
        return event

    async def delete_event(self, event_id: str) -> bool:
        initial_length = len(self.events)
        self.events = [event for event in self.events if event.id != event_id]
        return len(self.events) < initial_length
    