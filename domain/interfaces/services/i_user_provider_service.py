import datetime
from typing import Any, Dict, List, Optional, Protocol


class IUserProviderService(Protocol):
    def get_user_providers(self, user_id: str) -> List[Dict[str, Any]]:
        ...

    def set_user_providers(self, user_id: str, provider_ids: List[int]) -> List[Dict[str, Any]]:
        ...

    def get_onboarding_completed_at(self, user_id: str) -> Optional[datetime.datetime]:
        ...

    def complete_onboarding(self, user_id: str) -> Optional[datetime.datetime]:
        ...
