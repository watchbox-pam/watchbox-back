import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

from database.db import SessionLocal
from database.models import MediaProvider as DBMediaProvider
from database.models import User as DBUser
from database.models import t_user_media_provider
from domain.interfaces.repositories.i_user_provider_repository import IUserProviderRepository


class UserProviderRepository(IUserProviderRepository):
    def get_user_providers(self, user_id: str) -> List[Dict[str, Any]]:
        with SessionLocal() as session:
            rows = session.execute(
                select(DBMediaProvider.id, DBMediaProvider.name, DBMediaProvider.logo)
                .join(t_user_media_provider, t_user_media_provider.c.media_provider_id == DBMediaProvider.id)
                .where(t_user_media_provider.c.user_id == user_id)
                .order_by(DBMediaProvider.display_priority.asc().nulls_last(), DBMediaProvider.name)
            ).all()
        return [{"id": row.id, "name": row.name, "logo_path": row.logo} for row in rows]

    def replace_user_providers(self, user_id: str, providers: List[Dict[str, Any]]) -> None:
        # Une seule transaction : en cas d'erreur, l'ancienne sélection est conservée
        with SessionLocal() as session, session.begin():
            if providers:
                # media_provider.id = id TMDB : on ajoute au catalogue les plateformes qui n'y sont pas encore
                session.execute(
                    pg_insert(DBMediaProvider.__table__)
                    .values([
                        {
                            "id": p["id"],
                            "name": p.get("name") or "",
                            "logo": p.get("logo_path"),
                            "display_priority": p.get("display_priority"),
                        }
                        for p in providers
                    ])
                    .on_conflict_do_nothing(index_elements=["id"])
                )

            session.execute(delete(t_user_media_provider).where(t_user_media_provider.c.user_id == user_id))

            if providers:
                session.execute(
                    insert(t_user_media_provider),
                    [{"user_id": user_id, "media_provider_id": p["id"]} for p in providers]
                )

    def get_onboarding_completed_at(self, user_id: str) -> Optional[datetime.datetime]:
        with SessionLocal() as session:
            return session.scalar(select(DBUser.onboarding_completed_at).where(DBUser.id == user_id))

    def complete_onboarding(self, user_id: str) -> Optional[datetime.datetime]:
        with SessionLocal() as session, session.begin():
            session.execute(
                update(DBUser)
                .where(DBUser.id == user_id, DBUser.onboarding_completed_at.is_(None))
                .values(onboarding_completed_at=func.now())
            )
            return session.scalar(select(DBUser.onboarding_completed_at).where(DBUser.id == user_id))
