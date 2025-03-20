from typing import Optional

from domain.models.credits import Credits
from utils.tmdb_service import call_tmdb_api
from domain.interfaces.i_credits_repository import ICreditsRepository


class CreditsRepository(ICreditsRepository):
    def find_by_id(self, movie_id: int) -> Optional[Credits]:
        endpoint = f"/movie/{movie_id}/credits"

        result = call_tmdb_api(endpoint)

        credits = Credits(
            id=result["id"],
            cast=result["cast"],
            crew=result["crew"]
        )

        return credits