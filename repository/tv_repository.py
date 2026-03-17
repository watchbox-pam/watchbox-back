from typing import Optional, List

import db_config
from utils.tmdb_service import call_tmdb_api
from domain.interfaces.repositories.i_tv_repository import ITvRepository
from domain.models.tv import Tv

class TvRepository(ITvRepository):
    def find_by_id(self, tv_id: int) -> Optional[Tv]:
        endpoint = f"/tv/{tv_id}?language=fr-FR"

        result = call_tmdb_api(endpoint)

        tv = Tv(
            id=result.get("id"),
        )

        return tv
