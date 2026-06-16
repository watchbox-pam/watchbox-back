from datetime import datetime

from database.db import SessionLocal
from database.models.association_tables import t_swipe, t_review

DIRECTION_TO_RATING = {"like": 8, "dislike": 2}


class SwipeRepository:
    def create_swipe(self, user_id: str, movie_id: int, direction: str) -> dict:
        try:
            with SessionLocal() as session:
                existing = session.execute(
                    t_swipe.select().where(
                        t_swipe.c.user_id == user_id,
                        t_swipe.c.movie_id == movie_id
                    )
                ).first()

                if existing:
                    return {"is_duplicate": True}

                session.execute(t_swipe.insert().values(
                    user_id=user_id,
                    movie_id=movie_id,
                    direction=direction,
                    created_at=datetime.now()
                ))

                if direction in DIRECTION_TO_RATING:
                    session.execute(t_review.insert().values(
                        rating=DIRECTION_TO_RATING[direction],
                        comment=None,
                        has_spoiler_warning=False,
                        movie_id=movie_id,
                        tv_id=None,
                        tv_episode_id=None,
                        user_id=user_id,
                        created_at=datetime.now()
                    ))

                session.commit()
                return {"is_duplicate": False}
        except Exception as e:
            print(e)
            return {"is_duplicate": False, "error": str(e)}
