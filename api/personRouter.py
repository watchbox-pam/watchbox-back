from fastapi import APIRouter
from fastapi.params import Depends
from starlette.exceptions import HTTPException

from domain.interfaces.repositories.i_person_repository import IPersonRepository
from domain.interfaces.services.i_person_service import IPersonService
from service.person_service import PersonService
from repository.person_repository import PersonRepository

person_router = APIRouter(prefix="/person", tags=["Person"])

def get_person_service() -> IPersonService:
    repository: IPersonRepository = PersonRepository()
    return PersonService(repository)

@person_router.get("/{person_id}")
async def get_person_by_id(person_id: int, service: IPersonService = Depends(get_person_service)):
    """
    Returns the details for a person based on the person id
    :param person_id: the person id
    :param service: the service to call to get the info
    :return: the details of the person / or a 404 error if the id does not exist
    """
    person = service.find_by_id(person_id)
    if person:
        return person
    else:
        raise HTTPException(status_code=404, detail="Person not found")