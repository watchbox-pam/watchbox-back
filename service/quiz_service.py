import random
import threading
from typing import List

from domain.interfaces.repositories.i_quiz_repository import IQuizRepository
from domain.interfaces.services.i_quiz_service import IQuizService
from domain.models.quiz import (
    QuizQuestion, QuizAnswer, QuizResult, QuizQuestionResult,
    LeaderboardEntry, UserScores
)

GENRE_SLUG_TO_ID = {
    "horreur": 27,
    "aventure": 12,
    "action": 28,
    "comedie": 35,
    "drame": 18,
    "thriller": 53,
    "animation": 16,
    "romance": 10749
}

MIN_QUESTIONS = 30
QUESTIONS_PER_QUIZ = 10
BASE_POINTS = 100
MAX_SPEED_BONUS = 50
TIMER_SECONDS = 30


def _compute_level(score: int) -> int:
    return int(score ** 0.5 // 10)


def _speed_bonus(time_taken: float) -> int:
    if time_taken >= TIMER_SECONDS:
        return 0
    return int(MAX_SPEED_BONUS * (1 - time_taken / TIMER_SECONDS))


class QuizService(IQuizService):
    def __init__(self, repository: IQuizRepository):
        self.repository = repository

    def get_questions(self, genre_slug: str) -> List[QuizQuestion]:
        if genre_slug not in GENRE_SLUG_TO_ID:
            return []
        return self.repository.get_questions(genre_slug, QUESTIONS_PER_QUIZ)

    def generate_questions(self, genre_slug: str) -> None:
        if genre_slug not in GENRE_SLUG_TO_ID:
            return
        self._generate_questions(genre_slug)

    def submit_answers(self, user_id: str, genre_slug: str, answers: List[QuizAnswer]) -> QuizResult:
        question_ids = [a.question_id for a in answers]
        questions_map = {
            q.id: q for q in self.repository.get_questions_by_ids(question_ids)
        }

        question_results = []
        total_points = 0

        for answer in answers:
            question = questions_map.get(answer.question_id)
            if question is None:
                continue
            correct = answer.answer == question.correct_answer
            points = 0
            if correct:
                points = BASE_POINTS + _speed_bonus(answer.time_taken)
            total_points += points
            question_results.append(QuizQuestionResult(
                question_id=answer.question_id,
                correct=correct,
                points_earned=points,
                correct_answer=question.correct_answer
            ))

        new_genre_score = self.repository.upsert_score(user_id, genre_slug, total_points)
        new_global_score = self.repository.upsert_score(user_id, "global", total_points)

        return QuizResult(
            total_points=total_points,
            correct_count=sum(1 for r in question_results if r.correct),
            new_global_score=new_global_score,
            new_genre_score=new_genre_score,
            global_level=_compute_level(new_global_score),
            question_results=question_results
        )

    def get_leaderboard(self) -> List[LeaderboardEntry]:
        return self.repository.get_leaderboard(limit=20)

    def get_user_scores(self, user_id: str) -> UserScores:
        return self.repository.get_user_scores(user_id)

    def get_question_count(self, genre_slug: str) -> int:
        return self.repository.count_questions(genre_slug)

    def get_poster_paths(self, titles: List[str]) -> dict:
        return self.repository.get_poster_paths(titles)

    def trigger_generation(self, genre_slug: str) -> None:
        """Generate questions for a genre in a background daemon thread.
        Used by the routes so a request never blocks on generation."""
        threading.Thread(
            target=self.generate_questions, args=(genre_slug,), daemon=True
        ).start()

    def prewarm(self) -> List[str]:
        """Trigger background generation for every genre below the minimum.
        Returns the list of genres that started generating."""
        generating = []
        for slug in GENRE_SLUG_TO_ID:
            if self.repository.count_questions(slug) < MIN_QUESTIONS:
                self.trigger_generation(slug)
                generating.append(slug)
        return generating

    def get_status(self) -> dict:
        """Per-genre question count + whether the genre is ready to play."""
        counts = self.repository.count_questions_by_genre()
        return {
            slug: {
                "count": counts.get(slug, 0),
                "ready": counts.get(slug, 0) >= QUESTIONS_PER_QUIZ,
            }
            for slug in GENRE_SLUG_TO_ID
        }

    # ── Generation ──────────────────────────────────────────────────────────

    def _generate_questions(self, genre_slug: str) -> None:
        genre_id = GENRE_SLUG_TO_ID[genre_slug]
        questions = []

        print(f"[QUIZ] Génération {genre_slug} (genre_id={genre_id})…")
        movies = self.repository.get_movies_for_genre(genre_id)
        print(f"[QUIZ] {genre_slug} → {len(movies)} films trouvés")
        if not movies:
            print(f"[QUIZ] {genre_slug} → aucun film, génération annulée")
            return

        with_year = sum(1 for m in movies if m[6])
        with_poster = sum(1 for m in movies if m[3])
        with_backdrop = sum(1 for m in movies if m[2])
        with_director = sum(1 for m in movies if m[4])
        with_actor = sum(1 for m in movies if m[5])
        print(f"[QUIZ] {genre_slug} → year:{with_year} poster:{with_poster} backdrop:{with_backdrop} director:{with_director} actor:{with_actor}")

        all_titles = [m[1] for m in movies]
        poster_titles = [m[1] for m in movies if m[3] is not None]

        for movie in movies:
            (movie_id, title, backdrop, poster,
             director, main_actor, release_year,
             _original_title, budget, runtime) = movie

            image_path = backdrop or poster

            # Type: director
            if director:
                wrong = self.repository.get_directors_for_genre(genre_id, movie_id, 3)
                if len(wrong) == 3:
                    questions.append(self._build(
                        genre_slug, movie_id, "director",
                        f'Qui réalise le film "{title}" ?',
                        director, wrong, image_path
                    ))

            # Type: actor
            if main_actor:
                wrong = self.repository.get_actors_for_genre(genre_id, movie_id, 3)
                if len(wrong) == 3:
                    questions.append(self._build(
                        genre_slug, movie_id, "actor",
                        f'Quel acteur joue dans "{title}" ?',
                        main_actor, wrong, image_path
                    ))

            # Type: year
            if release_year:
                year = int(release_year)
                candidates = list({year - 3, year - 2, year - 1, year + 1, year + 2, year + 3})
                wrong = random.sample(candidates, 3)
                questions.append(self._build(
                    genre_slug, movie_id, "year",
                    f'En quelle année est sorti "{title}" ?',
                    str(year), [str(y) for y in wrong], image_path
                ))

            # Type: poster_guess
            if poster:
                wrong_titles = [t for t in poster_titles if t != title]
                if len(wrong_titles) >= 3:
                    wrong = random.sample(wrong_titles, 3)
                    questions.append(self._build(
                        genre_slug, movie_id, "poster_guess",
                        "De quel film s'agit-il ?",
                        title, wrong, backdrop
                    ))

            # Type: location_guess
            if backdrop:
                wrong_titles = [t for t in all_titles if t != title]
                if len(wrong_titles) >= 3:
                    wrong = random.sample(wrong_titles, 3)
                    questions.append(self._build(
                        genre_slug, movie_id, "location_guess",
                        "Quel film se déroule dans ce lieu ?",
                        title, wrong, backdrop
                    ))

            # Type: actor_not_in
            actors_in = self.repository.get_actors_in_film(movie_id, 3)
            if len(actors_in) >= 3:
                intruder = self.repository.get_actors_for_genre(genre_id, movie_id, 1)
                if intruder:
                    questions.append(self._build(
                        genre_slug, movie_id, "actor_not_in",
                        f'Lequel de ces acteurs ne joue PAS dans "{title}" ?',
                        intruder[0], actors_in[:3], image_path
                    ))

        # Type: film_not_by_director
        questions.extend(self._gen_film_not_by_director(genre_slug, genre_id))

        # Type: biggest_budget
        questions.extend(self._gen_comparison(genre_slug, movies, "budget"))

        # Type: oldest_film
        questions.extend(self._gen_comparison(genre_slug, movies, "oldest"))

        # Type: longest_film
        questions.extend(self._gen_comparison(genre_slug, movies, "runtime"))

        # Type: character_film
        questions.extend(self._gen_character(genre_slug, genre_id, all_titles))

        # Type: same_director
        questions.extend(self._gen_same_director(genre_slug, genre_id))

        print(f"[QUIZ] {genre_slug} → {len(questions)} questions générées, insertion…")
        self.repository.insert_questions(questions)
        print(f"[QUIZ] {genre_slug} → insertion terminée")

    def _gen_film_not_by_director(self, genre_slug: str, genre_id: int) -> list:
        questions = []
        director_groups = self.repository.get_directors_with_films_for_genre(genre_id, min_films=3)
        for director_name, film_titles, rep_movie_id in director_groups:
            if len(film_titles) < 3:
                continue
            film_not_by = self.repository.get_films_not_by_director(genre_id, director_name, rep_movie_id, 1)
            if not film_not_by:
                continue
            wrong = random.sample(film_titles, min(3, len(film_titles)))
            questions.append(self._build(
                genre_slug, rep_movie_id, "film_not_by_director",
                f"Lequel de ces films n'est PAS réalisé par {director_name} ?",
                film_not_by[0], wrong, None
            ))
        return questions

    def _gen_comparison(self, genre_slug: str, movies: list, compare: str) -> list:
        questions = []

        if compare == "budget":
            valid = [(m[0], m[1], m[2] or m[3], m[8]) for m in movies if m[8] and m[8] > 0]
            text = "Quel film a le plus gros budget ?"
            q_type = "biggest_budget"
            reverse = True
        elif compare == "oldest":
            valid = [(m[0], m[1], m[2] or m[3], m[6]) for m in movies if m[6]]
            text = "Lequel de ces films est sorti en premier ?"
            q_type = "oldest_film"
            reverse = False
        else:  # runtime
            valid = [(m[0], m[1], m[2] or m[3], m[9]) for m in movies if m[9] and m[9] > 0]
            text = "Quel film dure le plus longtemps ?"
            q_type = "longest_film"
            reverse = True

        if len(valid) < 4:
            return questions

        random.shuffle(valid)
        for i in range(0, len(valid) - 3, 4):
            group = valid[i:i + 4]
            if len(group) < 4:
                break
            sorted_group = sorted(group, key=lambda x: x[3], reverse=reverse)
            winner = sorted_group[0]
            others = sorted_group[1:]
            questions.append(self._build(
                genre_slug, winner[0], q_type,
                text,
                winner[1], [o[1] for o in others], None
            ))

        return questions

    def _gen_character(self, genre_slug: str, genre_id: int, all_titles: list) -> list:
        questions = []
        credits = self.repository.get_character_credits_for_genre(genre_id, 20)
        titles_pool = [c[2] for c in credits]

        for actor_name, char_name, movie_title, movie_id, image_path in credits:
            if not char_name:
                continue
            wrong_titles = [t for t in titles_pool if t != movie_title]
            if len(wrong_titles) < 3:
                wrong_titles = [t for t in all_titles if t != movie_title]
            if len(wrong_titles) >= 3:
                wrong = random.sample(wrong_titles, 3)
                questions.append(self._build(
                    genre_slug, movie_id, "character_film",
                    f'Dans quel film {actor_name} joue-t-il "{char_name}" ?',
                    movie_title, wrong, image_path
                ))

        return questions

    def _gen_same_director(self, genre_slug: str, genre_id: int) -> list:
        questions = []
        director_groups = self.repository.get_directors_with_films_for_genre(genre_id, min_films=4)
        all_director_names = [dg[0] for dg in director_groups]

        for director_name, film_titles, rep_movie_id in director_groups:
            if len(film_titles) < 4:
                continue
            sample_films = random.sample(film_titles, 4)
            films_str = " · ".join(f'"{f}"' for f in sample_films)
            wrong_directors = [d for d in all_director_names if d != director_name]
            if len(wrong_directors) < 3:
                wrong_directors = self.repository.get_directors_for_genre(genre_id, rep_movie_id, 3)
            if len(wrong_directors) >= 3:
                wrong = random.sample(wrong_directors, 3)
                questions.append(self._build(
                    genre_slug, rep_movie_id, "same_director",
                    f"Ces 4 films ont le même réalisateur : {films_str}. Qui est-ce ?",
                    director_name, wrong, None
                ))

        return questions

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _build(
        self, genre_slug: str, movie_id: int, q_type: str,
        text: str, correct: str, wrong: list, image_path
    ) -> dict:
        return {
            "genre_slug": genre_slug,
            "movie_id": movie_id,
            "question_type": q_type,
            "question_text": text,
            "correct_answer": correct,
            "wrong_answer_1": wrong[0],
            "wrong_answer_2": wrong[1],
            "wrong_answer_3": wrong[2],
            "image_path": image_path
        }
