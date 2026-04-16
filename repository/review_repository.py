from datetime import datetime
from typing import List

import db_config

from domain.interfaces.repositories.i_review_repository import IReviewRepository
from domain.models.review import Review, UserInfo
from database.db import SessionLocal
from database.models.user import User as DBUser
from database.models.association_tables import t_review


class ReviewRepository(IReviewRepository):
    def create_review(self, review: Review) -> bool:
        success: bool = False
        try:
            with SessionLocal() as session:
                new_review = t_review.insert().values(
                    rating=review.rating,
                    comment=review.comment,
                    has_spoiler_warning=review.isSpoiler,
                    movie_id=review.movieId,
                    tv_id=review.tvId,
                    tv_episode_id=review.tvEpisodeId,
                    user_id=review.userId,
                    created_at=datetime.now()
                )
                session.execute(new_review)
                session.commit()
                success = True
        except Exception as e:
            print(e)
        return success

    def get_reviews_by_media(self, media_id: int) -> List[Review]:
        reviews = []
        try:
            with SessionLocal() as session:
                results = session.query(
                    t_review.c.id,
                    t_review.c.rating,
                    t_review.c.comment,
                    t_review.c.has_spoiler_warning,
                    DBUser.username,
                    DBUser.profile_picture_path
                ).join(DBUser, DBUser.id == t_review.c.user_id).filter(
                    t_review.c.movie_id == media_id,
                    t_review.c.comment != None
                ).all()
                if results is not None:
                    for result in results:
                        reviews.append(Review(
                            id=result.id,
                            rating=result.rating,
                            comment=result.comment,
                            isSpoiler=result.has_spoiler_warning,
                            user=UserInfo(username=result.username, picture=result.profile_picture_path),
                            movieId=0,
                            tvId=0,
                            tvEpisodeId=0,
                            userId="",
                            createdAt=""
                        ))

        except Exception as e:
            print(e)

        return reviews

    def increment_counter(self) -> int:
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE ml_training_counter
                        SET new_ratings_count = new_ratings_count + 1
                        RETURNING new_ratings_count
                    """)
                    conn.commit()
                    return cur.fetchone()[0]
        except Exception as e:
            print(e)
            return 0

    def reset_counter(self) -> None:
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE ml_training_counter
                        SET new_ratings_count = 0,
                            last_trained_at = NOW()
                    """)
                    conn.commit()
        except Exception as e:
            print(e)