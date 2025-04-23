from typing import Optional

from domain.interfaces.repositories.i_person_repository import IPersonRepository
from domain.interfaces.services.i_person_service import IPersonService
from domain.models.person import PersonDetail
class PersonService(IPersonService):
    def __init__(self, repository: IPersonRepository):
        self.repository = repository

    def find_by_id(self, person_id: int) -> Optional[PersonDetail]:
        person, combined_credits = self.repository.find_by_id(person_id)

        return {
            "person": person,
            "combined_credits": combined_credits
        }
