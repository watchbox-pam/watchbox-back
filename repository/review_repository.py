from datetime import datetime
from typing import List

from sqlalchemy import func

from domain.interfaces.repositories.i_review_repository import IReviewRepository
from domain.models.review import Review, UserInfo
from database.db import SessionLocal
from database.models import t_review, t_ml_training_counter, User as DBUser


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
            with SessionLocal() as session:
                stmt = (
                    t_ml_training_counter.update()
                    .values(new_ratings_count=t_ml_training_counter.c.new_ratings_count + 1)
                    .returning(t_ml_training_counter.c.new_ratings_count)
                )
                new_count = session.execute(stmt).scalar()
                session.commit()
                return new_count or 0
        except Exception as e:
            print(e)
            return 0

    def reset_counter(self) -> None:
        try:
            with SessionLocal() as session:
                stmt = t_ml_training_counter.update().values(
                    new_ratings_count=0,
                    last_trained_at=func.now(),
                )
                session.execute(stmt)
                session.commit()
        except Exception as e:
            print(e)