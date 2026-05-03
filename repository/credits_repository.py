from typing import Optional

from domain.models.credits import Credits
from utils.tmdb_service import call_tmdb_api
from domain.interfaces.repositories.i_credits_repository import ICreditsRepository


class CreditsRepository(ICreditsRepository):
    def find_by_id(self, movie_id: int, include_adult: bool) -> Optional[Credits]:
        endpoint = f"/movie/{movie_id}/credits"

        result = call_tmdb_api(endpoint)

        credits = Credits(
            id=result["id"],
            cast=[member for member in result["cast"] if include_adult or not member["adult"]],
            crew=[member for member in result["crew"] if include_adult or not member["adult"]],
        )

        return credits