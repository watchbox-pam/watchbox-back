from typing import Optional, List

from domain.interfaces.repositories.i_tv_repository import ITvRepository
from domain.interfaces.services.i_tv_service import ITVService
from domain.models.tv import Tv

class TvService(ITVService):
    def __init__(self, repository: ITvRepository):
        self.repository = repository

    def find_by_id(self, tv_id: int) -> Optional[Tv]:
        return self.repository.find_by_id(tv_id)