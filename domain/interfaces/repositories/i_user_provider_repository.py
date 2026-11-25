import datetime
from typing import Any, Dict, List, Optional, Protocol


class IUserProviderRepository(Protocol):
    def get_user_providers(self, user_id: str) -> List[Dict[str, Any]]:
        """Plateformes de streaming sélectionnées par l'utilisateur."""
        ...

    def replace_user_providers(self, user_id: str, providers: List[Dict[str, Any]]) -> None:
        """Remplace toute la sélection de l'utilisateur (et ajoute au catalogue les plateformes absentes)."""
        ...

    def get_onboarding_completed_at(self, user_id: str) -> Optional[datetime.datetime]:
        ...

    def complete_onboarding(self, user_id: str) -> Optional[datetime.datetime]:
        """Marque l'onboarding comme terminé (sans écraser une date déjà présente)."""
        ...
