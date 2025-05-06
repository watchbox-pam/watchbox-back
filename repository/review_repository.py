from datetime import datetime

import db_config
from domain.interfaces.repositories.i_review_repository import IReviewRepository
from domain.models.review import Review


class ReviewRepository(IReviewRepository):
    def create_review(self, review: Review) -> bool:
        success: bool = False

        try:
            with db_config.connect_to_db() as conn:

                with conn.cursor() as cur:
                    query = ("INSERT INTO public.review"
                             "(rating, comment, has_spoiler_warning, movie_id, tv_id, tv_episode_id, user_id, created_at) "
                             "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);")

                    values = (review.rating, review.comment, review.has_spoiler, review.movie_id,
                              review.tv_id, review.tv_episode_id, review.user_id, datetime.now())

                    cur.execute(query, values)

                    success = True

        except (Exception) as e:
            print(e)

        return success