from typing import List

import db_config
from domain.interfaces.repositories.i_quiz_repository import IQuizRepository
from domain.models.quiz import QuizQuestion, LeaderboardEntry, UserScores, GenreScore


class QuizRepository(IQuizRepository):

    def get_questions(self, genre_slug: str, count: int) -> List[QuizQuestion]:
        questions = []
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, genre_slug, question_type, question_text, correct_answer,
                               wrong_answer_1, wrong_answer_2, wrong_answer_3, image_path
                        FROM quiz_question
                        WHERE genre_slug = %s
                        ORDER BY RANDOM()
                        LIMIT %s
                    """, (genre_slug, count))
                    for row in cur.fetchall():
                        wrong = [row[5], row[6], row[7]]
                        questions.append(QuizQuestion(
                            id=row[0],
                            genre_slug=row[1],
                            question_type=row[2],
                            question_text=row[3],
                            correct_answer=row[4],
                            wrong_answers=wrong,
                            image_path=row[8]
                        ))
        except Exception as e:
            print(e)
        return questions

    def count_questions(self, genre_slug: str) -> int:
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT COUNT(*) FROM quiz_question WHERE genre_slug = %s",
                        (genre_slug,)
                    )
                    return cur.fetchone()[0]
        except Exception as e:
            print(e)
            return 0

    def insert_questions(self, questions: list[dict]) -> None:
        if not questions:
            return
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    for q in questions:
                        try:
                            cur.execute("SAVEPOINT sp_quiz")
                            cur.execute("""
                                INSERT INTO quiz_question
                                    (genre_slug, movie_id, question_type, question_text,
                                     correct_answer, wrong_answer_1, wrong_answer_2, wrong_answer_3, image_path)
                                VALUES (%(genre_slug)s, %(movie_id)s, %(question_type)s, %(question_text)s,
                                        %(correct_answer)s, %(wrong_answer_1)s, %(wrong_answer_2)s,
                                        %(wrong_answer_3)s, %(image_path)s)
                            """, q)
                            cur.execute("RELEASE SAVEPOINT sp_quiz")
                        except Exception:
                            cur.execute("ROLLBACK TO SAVEPOINT sp_quiz")
                conn.commit()
        except Exception as e:
            print(e)

    def upsert_score(self, user_id: str, genre_slug: str, points: int) -> int:
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO quiz_score (user_id, genre_slug, total_score, games_played, updated_at)
                        VALUES (%s, %s, %s, 1, now())
                        ON CONFLICT (user_id, genre_slug)
                        DO UPDATE SET
                            total_score = quiz_score.total_score + EXCLUDED.total_score,
                            games_played = quiz_score.games_played + 1,
                            updated_at = now()
                        RETURNING total_score
                    """, (user_id, genre_slug, points))
                    new_score = cur.fetchone()[0]
                conn.commit()
                return new_score
        except Exception as e:
            print(e)
            return 0

    def get_leaderboard(self, limit: int = 20) -> List[LeaderboardEntry]:
        entries = []
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT qs.user_id, u.username, u.profile_picture_path,
                               qs.total_score
                        FROM quiz_score qs
                        JOIN "user" u ON u.id = qs.user_id
                        WHERE qs.genre_slug = 'global'
                        ORDER BY qs.total_score DESC
                        LIMIT %s
                    """, (limit,))
                    for rank, row in enumerate(cur.fetchall(), start=1):
                        score = row[3]
                        entries.append(LeaderboardEntry(
                            rank=rank,
                            user_id=str(row[0]),
                            username=row[1],
                            picture=row[2],
                            total_score=score,
                            level=int(score ** 0.5 // 10)
                        ))
        except Exception as e:
            print(e)
        return entries

    def get_user_scores(self, user_id: str) -> UserScores:
        global_score = 0
        genre_scores = []
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT genre_slug, total_score, games_played
                        FROM quiz_score
                        WHERE user_id = %s
                    """, (user_id,))
                    for row in cur.fetchall():
                        if row[0] == "global":
                            global_score = row[1]
                        else:
                            genre_scores.append(GenreScore(
                                genre_slug=row[0],
                                total_score=row[1],
                                games_played=row[2]
                            ))
        except Exception as e:
            print(e)
        return UserScores(
            global_score=global_score,
            global_level=int(global_score ** 0.5 // 10),
            genre_scores=genre_scores
        )

    def get_questions_by_ids(self, question_ids: list[int]) -> List[QuizQuestion]:
        questions = []
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, genre_slug, question_type, question_text, correct_answer,
                               wrong_answer_1, wrong_answer_2, wrong_answer_3, image_path
                        FROM quiz_question
                        WHERE id = ANY(%s)
                    """, (question_ids,))
                    for row in cur.fetchall():
                        questions.append(QuizQuestion(
                            id=row[0],
                            genre_slug=row[1],
                            question_type=row[2],
                            question_text=row[3],
                            correct_answer=row[4],
                            wrong_answers=[row[5], row[6], row[7]],
                            image_path=row[8]
                        ))
        except Exception as e:
            print(e)
        return questions

    def get_directors_for_genre(self, genre_id: int, exclude_movie_id: int, limit: int) -> List[str]:
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT name FROM (
                            SELECT DISTINCT p.name
                            FROM credit c
                            JOIN person p ON p.id = c.person_id
                            JOIN movie_movie_genre mg ON mg.movie_id = c.movie_id
                            WHERE c.job_id = 537
                              AND mg.genre_id = %s
                              AND c.movie_id != %s
                              AND p.name IS NOT NULL
                        ) t ORDER BY RANDOM() LIMIT %s
                    """, (genre_id, exclude_movie_id, limit))
                    return [row[0] for row in cur.fetchall()]
        except Exception as e:
            print(e)
            return []

    def get_actors_for_genre(self, genre_id: int, exclude_movie_id: int, limit: int) -> List[str]:
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT name FROM (
                            SELECT DISTINCT p.name
                            FROM credit c
                            JOIN person p ON p.id = c.person_id
                            JOIN movie_movie_genre mg ON mg.movie_id = c.movie_id
                            WHERE c.job_id = 96
                              AND c.order <= 2
                              AND mg.genre_id = %s
                              AND c.movie_id != %s
                              AND p.name IS NOT NULL
                        ) t ORDER BY RANDOM() LIMIT %s
                    """, (genre_id, exclude_movie_id, limit))
                    return [row[0] for row in cur.fetchall()]
        except Exception as e:
            print(e)
            return []

    def get_original_titles_for_genre(self, genre_id: int, exclude_movie_id: int, limit: int) -> List[str]:
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT original_title FROM (
                            SELECT DISTINCT m.original_title
                            FROM movie m
                            JOIN movie_movie_genre mg ON mg.movie_id = m.id
                            WHERE mg.genre_id = %s
                              AND m.id != %s
                              AND m.original_title IS NOT NULL
                              AND m.original_title != m.title
                        ) t ORDER BY RANDOM() LIMIT %s
                    """, (genre_id, exclude_movie_id, limit))
                    return [row[0] for row in cur.fetchall()]
        except Exception as e:
            print(e)
            return []

    def get_actors_in_film(self, movie_id: int, limit: int) -> List[str]:
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT p.name
                        FROM credit c
                        JOIN person p ON p.id = c.person_id
                        WHERE c.movie_id = %s
                          AND c.job_id = 96
                          AND c.order <= 5
                          AND p.name IS NOT NULL
                        GROUP BY p.name
                        ORDER BY MIN(c.order)
                        LIMIT %s
                    """, (movie_id, limit))
                    return [row[0] for row in cur.fetchall()]
        except Exception as e:
            print(e)
            return []

    def get_films_not_by_director(self, genre_id: int, director_name: str, exclude_movie_id: int, limit: int) -> List[str]:
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT title FROM (
                            SELECT DISTINCT m.title
                            FROM movie m
                            JOIN movie_movie_genre mg ON mg.movie_id = m.id
                            WHERE mg.genre_id = %s
                              AND m.id != %s
                              AND m.title IS NOT NULL
                              AND m.id NOT IN (
                                  SELECT c2.movie_id
                                  FROM credit c2
                                  JOIN person p2 ON p2.id = c2.person_id
                                  WHERE c2.job_id = 537 AND p2.name = %s
                              )
                        ) t ORDER BY RANDOM() LIMIT %s
                    """, (genre_id, exclude_movie_id, director_name, limit))
                    return [row[0] for row in cur.fetchall()]
        except Exception as e:
            print(e)
            return []

    def get_directors_with_films_for_genre(self, genre_id: int, min_films: int) -> List[tuple]:
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT p.name,
                               array_agg(DISTINCT m.title) AS titles,
                               MIN(m.id) AS rep_movie_id
                        FROM credit c
                        JOIN person p ON p.id = c.person_id
                        JOIN movie m ON m.id = c.movie_id
                        JOIN movie_movie_genre mg ON mg.movie_id = m.id
                        WHERE c.job_id = 537
                          AND mg.genre_id = %s
                          AND p.name IS NOT NULL
                          AND m.title IS NOT NULL
                        GROUP BY p.name
                        HAVING COUNT(DISTINCT m.id) >= %s
                        ORDER BY RANDOM()
                        LIMIT 15
                    """, (genre_id, min_films))
                    return [(row[0], row[1], row[2]) for row in cur.fetchall()]
        except Exception as e:
            print(e)
            return []

    def get_character_credits_for_genre(self, genre_id: int, limit: int) -> List[tuple]:
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT p.name,
                               c.character,
                               m.title,
                               m.id,
                               COALESCE(m.backdrop_path, m.poster_path)
                        FROM credit c
                        JOIN person p ON p.id = c.person_id
                        JOIN movie m ON m.id = c.movie_id
                        JOIN movie_movie_genre mg ON mg.movie_id = m.id
                        WHERE c.job_id = 96
                          AND c.order <= 3
                          AND c.character IS NOT NULL
                          AND c.character != ''
                          AND mg.genre_id = %s
                          AND p.name IS NOT NULL
                          AND m.title IS NOT NULL
                        ORDER BY RANDOM()
                        LIMIT %s
                    """, (genre_id, limit))
                    return [(row[0], row[1], row[2], row[3], row[4]) for row in cur.fetchall()]
        except Exception as e:
            print(e)
            return []
