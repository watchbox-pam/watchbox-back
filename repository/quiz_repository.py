from typing import List, Optional

from sqlalchemy import Integer, and_, case, cast, distinct, func, or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from database.db import SessionLocal
from database.models import (
    Movie,
    Person,
    User,
    t_credit,
    t_movie_movie_genre,
    t_quiz_question,
    t_quiz_score,
)
from domain.interfaces.repositories.i_quiz_repository import IQuizRepository
from domain.models.quiz import GenreScore, LeaderboardEntry, QuizQuestion, UserScores

JOB_ID_DIRECTOR = 537
JOB_ID_ACTOR = 96


class QuizRepository(IQuizRepository):

    def get_questions(self, genre_slug: str, count: int) -> List[QuizQuestion]:
        questions = []
        try:
            with SessionLocal() as session:
                
                image_expr = case(
                    (
                        t_quiz_question.c.question_type.in_(
                            ["same_director", "film_not_by_director"]
                        ),
                        t_quiz_question.c.image_path,
                    ),
                    else_=func.coalesce(
                        t_quiz_question.c.image_path,
                        Movie.backdrop_path,
                        Movie.poster_path,
                    ),
                ).label("image_path")
                stmt = (
                    select(
                        t_quiz_question.c.id,
                        t_quiz_question.c.genre_slug,
                        t_quiz_question.c.question_type,
                        t_quiz_question.c.question_text,
                        t_quiz_question.c.correct_answer,
                        t_quiz_question.c.wrong_answer_1,
                        t_quiz_question.c.wrong_answer_2,
                        t_quiz_question.c.wrong_answer_3,
                        image_expr,
                    )
                    .select_from(
                        t_quiz_question.join(
                            Movie.__table__,
                            Movie.id == t_quiz_question.c.movie_id,
                            isouter=True,
                        )
                    )
                    .where(t_quiz_question.c.genre_slug == genre_slug)
                    .order_by(func.random())
                    .limit(count)
                )
                for row in session.execute(stmt):
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

    def count_questions(self, genre_slug: str) -> int:
        try:
            with SessionLocal() as session:
                stmt = (
                    select(func.count())
                    .select_from(t_quiz_question)
                    .where(t_quiz_question.c.genre_slug == genre_slug)
                )
                return session.execute(stmt).scalar() or 0
        except Exception as e:
            print(e)
            return 0

    def count_questions_by_genre(self) -> dict:
        counts = {}
        try:
            with SessionLocal() as session:
                stmt = (
                    select(t_quiz_question.c.genre_slug, func.count())
                    .group_by(t_quiz_question.c.genre_slug)
                )
                for slug, n in session.execute(stmt):
                    counts[slug] = n
        except Exception as e:
            print(e)
        return counts

    def insert_questions(self, questions: list[dict]) -> None:
        if not questions:
            return
        try:
            with SessionLocal() as session:
                for q in questions:
                    try:
                        with session.begin_nested():
                            session.execute(t_quiz_question.insert().values(**q))
                    except Exception:
                        pass
                session.commit()
        except Exception as e:
            print(e)

    def upsert_score(self, user_id: str, genre_slug: str, points: int) -> int:
        try:
            with SessionLocal() as session:
                stmt = pg_insert(t_quiz_score).values(
                    user_id=user_id,
                    genre_slug=genre_slug,
                    total_score=points,
                    games_played=1,
                    updated_at=func.now(),
                )
                stmt = stmt.on_conflict_do_update(
                    index_elements=["user_id", "genre_slug"],
                    set_={
                        "total_score": t_quiz_score.c.total_score + stmt.excluded.total_score,
                        "games_played": t_quiz_score.c.games_played + 1,
                        "updated_at": func.now(),
                    },
                ).returning(t_quiz_score.c.total_score)
                new_score = session.execute(stmt).scalar()
                session.commit()
                return new_score or 0
        except Exception as e:
            print(e)
            return 0

    def get_leaderboard(self, limit: int = 20) -> List[LeaderboardEntry]:
        entries = []
        try:
            with SessionLocal() as session:
                stmt = (
                    select(
                        t_quiz_score.c.user_id,
                        User.username,
                        User.profile_picture_path,
                        t_quiz_score.c.total_score,
                    )
                    .select_from(t_quiz_score.join(User, User.id == t_quiz_score.c.user_id))
                    .where(t_quiz_score.c.genre_slug == "global")
                    .order_by(t_quiz_score.c.total_score.desc())
                    .limit(limit)
                )
                for rank, row in enumerate(session.execute(stmt), start=1):
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
            with SessionLocal() as session:
                stmt = (
                    select(
                        t_quiz_score.c.genre_slug,
                        t_quiz_score.c.total_score,
                        t_quiz_score.c.games_played,
                    )
                    .where(t_quiz_score.c.user_id == user_id)
                )
                for row in session.execute(stmt):
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
            with SessionLocal() as session:
                stmt = (
                    select(
                        t_quiz_question.c.id,
                        t_quiz_question.c.genre_slug,
                        t_quiz_question.c.question_type,
                        t_quiz_question.c.question_text,
                        t_quiz_question.c.correct_answer,
                        t_quiz_question.c.wrong_answer_1,
                        t_quiz_question.c.wrong_answer_2,
                        t_quiz_question.c.wrong_answer_3,
                        t_quiz_question.c.image_path,
                    )
                    .where(t_quiz_question.c.id.in_(question_ids))
                )
                for row in session.execute(stmt):
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
            with SessionLocal() as session:

                subq = (
                    select(Person.name.label("name"))
                    .distinct()
                    .select_from(
                        t_credit
                        .join(Person, Person.id == t_credit.c.person_id)
                        .join(t_movie_movie_genre, t_movie_movie_genre.c.movie_id == t_credit.c.movie_id)
                    )
                    .where(
                        t_credit.c.job_id == JOB_ID_DIRECTOR,
                        t_movie_movie_genre.c.genre_id == genre_id,
                        t_credit.c.movie_id != exclude_movie_id,
                        Person.name.isnot(None),
                    )
                    .subquery()
                )
                stmt = select(subq.c.name).order_by(func.random()).limit(limit)
                return [row[0] for row in session.execute(stmt)]
        except Exception as e:
            print(e)
            return []

    def get_actors_for_genre(self, genre_id: int, exclude_movie_id: int, limit: int) -> List[str]:
        try:
            with SessionLocal() as session:
                subq = (
                    select(Person.name.label("name"))
                    .distinct()
                    .select_from(
                        t_credit
                        .join(Person, Person.id == t_credit.c.person_id)
                        .join(t_movie_movie_genre, t_movie_movie_genre.c.movie_id == t_credit.c.movie_id)
                    )
                    .where(
                        t_credit.c.job_id == JOB_ID_ACTOR,
                        t_credit.c.order <= 2,
                        t_movie_movie_genre.c.genre_id == genre_id,
                        t_credit.c.movie_id != exclude_movie_id,
                        Person.name.isnot(None),
                    )
                    .subquery()
                )
                stmt = select(subq.c.name).order_by(func.random()).limit(limit)
                return [row[0] for row in session.execute(stmt)]
        except Exception as e:
            print(e)
            return []

    def get_original_titles_for_genre(self, genre_id: int, exclude_movie_id: int, limit: int) -> List[str]:
        try:
            with SessionLocal() as session:
                subq = (
                    select(Movie.original_title.label("original_title"))
                    .distinct()
                    .select_from(
                        Movie.__table__
                        .join(t_movie_movie_genre, t_movie_movie_genre.c.movie_id == Movie.id)
                    )
                    .where(
                        t_movie_movie_genre.c.genre_id == genre_id,
                        Movie.id != exclude_movie_id,
                        Movie.original_title.isnot(None),
                        Movie.original_title != Movie.title,
                    )
                    .subquery()
                )
                stmt = select(subq.c.original_title).order_by(func.random()).limit(limit)
                return [row[0] for row in session.execute(stmt)]
        except Exception as e:
            print(e)
            return []

    def get_actors_in_film(self, movie_id: int, limit: int) -> List[str]:
        try:
            with SessionLocal() as session:
                stmt = (
                    select(Person.name)
                    .select_from(t_credit.join(Person, Person.id == t_credit.c.person_id))
                    .where(
                        t_credit.c.movie_id == movie_id,
                        t_credit.c.job_id == JOB_ID_ACTOR,
                        t_credit.c.order <= 5,
                        Person.name.isnot(None),
                    )
                    .group_by(Person.name)
                    .order_by(func.min(t_credit.c.order))
                    .limit(limit)
                )
                return [row[0] for row in session.execute(stmt)]
        except Exception as e:
            print(e)
            return []

    def get_films_not_by_director(self, genre_id: int, director_name: str, exclude_movie_id: int, limit: int) -> List[str]:
        try:
            with SessionLocal() as session:
                directed_by = (
                    select(t_credit.c.movie_id)
                    .select_from(t_credit.join(Person, Person.id == t_credit.c.person_id))
                    .where(
                        t_credit.c.job_id == JOB_ID_DIRECTOR,
                        Person.name == director_name,
                    )
                )
                subq = (
                    select(Movie.title.label("title"))
                    .distinct()
                    .select_from(
                        Movie.__table__
                        .join(t_movie_movie_genre, t_movie_movie_genre.c.movie_id == Movie.id)
                    )
                    .where(
                        t_movie_movie_genre.c.genre_id == genre_id,
                        Movie.id != exclude_movie_id,
                        Movie.title.isnot(None),
                        Movie.id.notin_(directed_by),
                    )
                    .subquery()
                )
                stmt = select(subq.c.title).order_by(func.random()).limit(limit)
                return [row[0] for row in session.execute(stmt)]
        except Exception as e:
            print(e)
            return []

    def get_directors_with_films_for_genre(self, genre_id: int, min_films: int) -> List[tuple]:
        try:
            with SessionLocal() as session:
                stmt = (
                    select(
                        Person.name,
                        func.array_agg(distinct(Movie.title)).label("titles"),
                        func.min(Movie.id).label("rep_movie_id"),
                    )
                    .select_from(
                        t_credit
                        .join(Person, Person.id == t_credit.c.person_id)
                        .join(Movie.__table__, Movie.id == t_credit.c.movie_id)
                        .join(t_movie_movie_genre, t_movie_movie_genre.c.movie_id == Movie.id)
                    )
                    .where(
                        t_credit.c.job_id == JOB_ID_DIRECTOR,
                        t_movie_movie_genre.c.genre_id == genre_id,
                        Person.name.isnot(None),
                        Movie.title.isnot(None),
                    )
                    .group_by(Person.name)
                    .having(func.count(distinct(Movie.id)) >= min_films)
                    .order_by(func.random())
                    .limit(15)
                )
                return [(row[0], row[1], row[2]) for row in session.execute(stmt)]
        except Exception as e:
            print(e)
            return []

    def get_character_credits_for_genre(self, genre_id: int, limit: int) -> List[tuple]:
        try:
            with SessionLocal() as session:
                stmt = (
                    select(
                        Person.name,
                        t_credit.c.character,
                        Movie.title,
                        Movie.id,
                        func.coalesce(Movie.backdrop_path, Movie.poster_path),
                    )
                    .select_from(
                        t_credit
                        .join(Person, Person.id == t_credit.c.person_id)
                        .join(Movie.__table__, Movie.id == t_credit.c.movie_id)
                        .join(t_movie_movie_genre, t_movie_movie_genre.c.movie_id == Movie.id)
                    )
                    .where(
                        t_credit.c.job_id == JOB_ID_ACTOR,
                        t_credit.c.order <= 3,
                        t_credit.c.character.isnot(None),
                        t_credit.c.character != "",
                        t_movie_movie_genre.c.genre_id == genre_id,
                        Person.name.isnot(None),
                        Movie.title.isnot(None),
                    )
                    .order_by(func.random())
                    .limit(limit)
                )
                return [(row[0], row[1], row[2], row[3], row[4]) for row in session.execute(stmt)]
        except Exception as e:
            print(e)
            return []

    def get_poster_paths(self, titles: list[str]) -> dict[str, Optional[str]]:
        try:
            with SessionLocal() as session:
                stmt = (
                    select(Movie.title, Movie.poster_path)
                    .distinct(Movie.title)
                    .where(
                        Movie.title.in_(titles),
                        Movie.poster_path.isnot(None),
                    )
                    .order_by(Movie.title, Movie.popularity.desc().nullslast())
                )
                return {row[0]: row[1] for row in session.execute(stmt)}
        except Exception as e:
            print(e)
            return {}

    def get_movies_for_genre(self, genre_id: int, limit: int = 50) -> List[tuple]:
        # Returns, per movie: (id, title, backdrop, poster, director, main_actor,
        #                       release_year, original_title, budget, runtime)
        try:
            with SessionLocal() as session:
                stmt = (
                    select(
                        Movie.id,
                        Movie.title,
                        Movie.backdrop_path,
                        Movie.poster_path,
                        func.max(case((t_credit.c.job_id == JOB_ID_DIRECTOR, Person.name))).label("director"),
                        func.max(case((and_(t_credit.c.job_id == JOB_ID_ACTOR, t_credit.c.order == 0), Person.name))).label("main_actor"),
                        cast(func.extract("year", Movie.release_date), Integer).label("release_year"),
                        Movie.original_title,
                        Movie.budget,
                        Movie.runtime,
                    )
                    .select_from(
                        Movie.__table__
                        .join(t_movie_movie_genre, t_movie_movie_genre.c.movie_id == Movie.id)
                        .join(
                            t_credit,
                            and_(
                                t_credit.c.movie_id == Movie.id,
                                or_(
                                    t_credit.c.job_id == JOB_ID_DIRECTOR,
                                    and_(t_credit.c.job_id == JOB_ID_ACTOR, t_credit.c.order == 0),
                                ),
                            ),
                            isouter=True,
                        )
                        .join(Person, Person.id == t_credit.c.person_id, isouter=True)
                    )
                    .where(
                        t_movie_movie_genre.c.genre_id == genre_id,
                        Movie.title.isnot(None),
                    )
                    .group_by(
                        Movie.id, Movie.title, Movie.backdrop_path, Movie.poster_path,
                        Movie.release_date, Movie.original_title, Movie.popularity,
                        Movie.budget, Movie.runtime,
                    )
                    .order_by(Movie.popularity.desc())
                    .limit(limit)
                )
                return [tuple(row) for row in session.execute(stmt)]
        except Exception as e:
            print(e)
            return []
