from typing import List
from datetime import date, datetime
from domain.interfaces.services.i_calendar_service import ICalendarService
from domain.interfaces.repositories.i_event_repository import IEventRepository
from domain.interfaces.repositories.i_film_festival_repository import IFilmFestivalRepository
from domain.models.event import Event, EventCreate
from domain.models.filmFestivals import FilmFestival

class CalendarService(ICalendarService):
    def __init__(
        self,
        event_repository: IEventRepository,
        festival_repository: IFilmFestivalRepository
    ):
        self.event_repository = event_repository
        self.festival_repository = festival_repository

    def _format_date_to_string(self, date_obj: date) -> str:
        """Formate une date en string DD-MM-YYYY"""
        return date_obj.strftime("%d-%m-%Y")

    def _parse_date_string(self, date_str: str) -> date:
        """Parse une string DD-MM-YYYY en date"""
        return datetime.strptime(date_str, "%d-%m-%Y").date()

    async def get_events_for_date(self, date_obj: date) -> List[Event]:
        date_str = self._format_date_to_string(date_obj)
        return await self.event_repository.get_events_by_date(date_str)

    async def get_festivals_for_date(self, date_obj: date) -> List[FilmFestival]:
        festivals = await self.festival_repository.get_all_festivals()
        
        filtered_festivals = []
        for festival in festivals:
            start_date = self._parse_date_string(festival.start_date)
            end_date = self._parse_date_string(festival.end_date)
            
            if start_date <= date_obj <= end_date:
                filtered_festivals.append(festival)
        
        return filtered_festivals

    async def has_events_on_date(self, date_obj: date) -> bool:
        events = await self.get_events_for_date(date_obj)
        festivals = await self.get_festivals_for_date(date_obj)
        return len(events) > 0 or len(festivals) > 0

    async def create_event(self, event_data: EventCreate) -> Event:
        # Génère un ID unique
        event_id = str(int(datetime.now().timestamp() * 1000))
        
        event = Event(
            id=event_id,
            **event_data.model_dump()
        )
        
        return await self.event_repository.create_event(event)

    async def delete_event(self, event_id: str) -> bool:
        return await self.event_repository.delete_event(event_id)