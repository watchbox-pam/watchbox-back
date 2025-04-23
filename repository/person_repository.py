from typing import Optional

from domain.interfaces.repositories.i_person_repository import IPersonRepository
from domain.models.person import PersonDetail
from utils.tmdb_service import call_tmdb_api
from domain.models.combined_credits import CombinedCredits

class PersonRepository(IPersonRepository):
    def find_by_id(self, person_id: int) -> Optional[PersonDetail]:
        endpoint = f"/person/{person_id}?append_to_response=combined_credits&language=fr-FR"

        result = call_tmdb_api(endpoint)

        person = {
            "id": result["id"],
            "biography": result["biography"],
            "birthday": result["birthday"],
            "deathday": result["deathday"],
            "name": result["name"],
            "place_of_birth": result["place_of_birth"],
            "profile_path": result["profile_path"],
        }
        

        refactored_cast = [
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "poster_path": item.get("poster_path"),
                "media_type": item.get("media_type"),
                "popularity": item.get("popularity")
            }
            for item in result["combined_credits"]["cast"]
        ]
        refactored_cast = sorted(refactored_cast, key=lambda x: x.get("popularity", 0), reverse=True)

        refactored_crew = [
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "poster_path": item.get("poster_path"),
                "media_type": item.get("media_type"),
                "popularity": item.get("popularity")
            }
            for item in result["combined_credits"]["crew"]
        ]
        refactored_crew = sorted(refactored_crew, key=lambda x: x.get("popularity", 0), reverse=True)

        combined_credits = {
            "cast": refactored_cast,
            "crew": refactored_crew,
        }

        return person, combined_credits