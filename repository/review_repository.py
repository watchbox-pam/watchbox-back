from datetime import datetime
from typing import List

import db_config
from domain.interfaces.repositories.i_review_repository import IReviewRepository
from domain.models.review import Review, UserInfo


class ReviewRepository(IReviewRepository):
    def create_review(self, review: Review) -> bool:
        success: bool = False

        try:
            with db_config.connect_to_db() as conn:

                with conn.cursor() as cur:
                    query = ("INSERT INTO public.review"
                             "(rating, comment, has_spoiler_warning, movie_id, tv_id, tv_episode_id, user_id, created_at) "
                             "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);")

                    values = (review.rating, review.comment, review.isSpoiler, review.movieId,
                              review.tvId, review.tvEpisodeId, review.userId, datetime.now())

                    cur.execute(query, values)

                    success = True

        except (Exception) as e:
            print(e)

        return success


    def get_reviews_by_media(self, media_id: int) -> List[Review]:
        reviews = []

        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT R.id, R.rating, R.comment, R.has_spoiler_warning, U.username, U.profile_picture_path FROM public.review R "
"INNER JOIN public.user U ON U.id = R.user_id WHERE R.movie_id = %s AND R.comment IS NOT NULL", (media_id,))
                    results = cur.fetchall()

                    if results is not None:
                        for result in results:
                            reviews.append(Review(
                                id=result[0],
                                rating=result[1],
                                comment=result[2],
                                isSpoiler=result[3],
                                user=UserInfo(username=result[4], picture=result[5]),
                                movieId=0,
                                tvId=0,
                                tvEpisodeId=0,
                                userId="",
                                createdAt=""
                            ))

        except Exception as e:
            print(e)

        return reviews