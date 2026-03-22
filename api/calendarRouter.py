from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import date
from domain.models.event import Event, EventCreate
from domain.models.filmFestivals import FilmFestival
from service.calendar_service import CalendarService
from repository.event_repository import EventRepository
from repository.film_festival_repository import FilmFestivalRepository

router = APIRouter(prefix="/calendar", tags=["calendar"])

# Dependency injection
def get_calendar_service() -> CalendarService:
    event_repo = EventRepository()
    festival_repo = FilmFestivalRepository()
    return CalendarService(event_repo, festival_repo)

@router.get("/events/{date}", response_model=List[Event])
async def get_events(
    date: date,
    service: CalendarService = Depends(get_calendar_service)
):
    """Récupère les événements pour une date donnée"""
    return await service.get_events_for_date(date)

@router.get("/festivals/{date}", response_model=List[FilmFestival])
async def get_festivals(
    date: date,
    service: CalendarService = Depends(get_calendar_service)
):
    """Récupère les festivals pour une date donnée"""
    return await service.get_festivals_for_date(date)

@router.get("/has-events/{date}", response_model=bool)
async def has_events(
    date: date,
    service: CalendarService = Depends(get_calendar_service)
):
    """Vérifie si une date a des événements"""
    return await service.has_events_on_date(date)

@router.post("/events", response_model=Event)
async def create_event(
    event_data: EventCreate,
    service: CalendarService = Depends(get_calendar_service)
):
    """Crée un nouvel événement"""
    return await service.create_event(event_data)

@router.delete("/events/{event_id}", response_model=bool)
async def delete_event(
    event_id: str,
    service: CalendarService = Depends(get_calendar_service)
):
    """Supprime un événement"""
    success = await service.delete_event(event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
    return success

@router.get("/festivals", response_model=List[FilmFestival])
async def get_all_festivals(
    service: CalendarService = Depends(get_calendar_service)
):
    """Récupère tous les festivals"""
    return await service.festival_repository.get_all_festivals()