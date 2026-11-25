import datetime
from typing import Any, Dict, List, Optional

from domain.interfaces.repositories.i_provider_repository import IProviderRepository
from domain.interfaces.repositories.i_user_provider_repository import IUserProviderRepository
from domain.interfaces.services.i_user_provider_service import IUserProviderService
from domain.models.providerErrors import InvalidProviderError, ProviderCatalogUnavailableError


class UserProviderService(IUserProviderService):
    def __init__(self, repository: IUserProviderRepository, provider_repository: IProviderRepository):
        self.repository = repository
        self.provider_repository = provider_repository

    def get_user_providers(self, user_id: str) -> List[Dict[str, Any]]:
        return self.repository.get_user_providers(user_id)

    def set_user_providers(self, user_id: str, provider_ids: List[int]) -> List[Dict[str, Any]]:
        # Doublons retirés, ordre conservé
        wanted = list(dict.fromkeys(provider_ids))

        providers: List[Dict[str, Any]] = []
        if wanted:
            # Même liste que GET /providers (TMDB, France) : on n'accepte que des ids qui y figurent
            catalog = {p["id"]: p for p in self.provider_repository.get_providers() if p.get("id") is not None}
            if not catalog:
                raise ProviderCatalogUnavailableError()

            unknown = [provider_id for provider_id in wanted if provider_id not in catalog]
            if unknown:
                raise InvalidProviderError(unknown)

            providers = [catalog[provider_id] for provider_id in wanted]

        self.repository.replace_user_providers(user_id, providers)
        return self.repository.get_user_providers(user_id)

    def get_onboarding_completed_at(self, user_id: str) -> Optional[datetime.datetime]:
        return self.repository.get_onboarding_completed_at(user_id)

    def complete_onboarding(self, user_id: str) -> Optional[datetime.datetime]:
        return self.repository.complete_onboarding(user_id)
