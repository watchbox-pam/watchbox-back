import random
import threading
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.auth.verify_auth_token import check_jwt_token
from domain.interfaces.services.i_quiz_service import IQuizService
from repository.quiz_repository import QuizRepository
from service.quiz_service import QuizService, GENRE_SLUG_TO_ID

quiz_router = APIRouter(prefix="/quiz", tags=["quiz"])


def get_quiz_service() -> IQuizService:
    return QuizService(QuizRepository())


class AnswerPayload(BaseModel):
    question_id: int
    answer: str
    time_taken: float


class SubmitPayload(BaseModel):
    genre_slug: str
    answers: list[AnswerPayload]


@quiz_router.get("/questions/{genre_slug}")
def get_questions(
    genre_slug: str,
    user_id: str = Depends(check_jwt_token)
):
    if genre_slug not in GENRE_SLUG_TO_ID:
        raise HTTPException(status_code=404, detail="Genre inconnu")

    repo = QuizRepository()
    count = repo.count_questions(genre_slug)

    if count == 0:
        threading.Thread(
            target=lambda: QuizService(QuizRepository()).generate_questions(genre_slug),
            daemon=True
        ).start()
        raise HTTPException(
            status_code=503,
            detail="Questions en cours de préparation, réessaie dans quelques secondes."
        )

    if count < 30:
        threading.Thread(
            target=lambda: QuizService(QuizRepository()).generate_questions(genre_slug),
            daemon=True
        ).start()

    questions = repo.get_questions(genre_slug, 10)
    result = []
    for q in questions:
        answers, answer_images = _shuffle_with_images(q.correct_answer, q.wrong_answers, q.question_type)
        result.append({
            "id": q.id,
            "question_type": q.question_type,
            "question_text": q.question_text,
            "answers": answers,
            "answer_images": answer_images,
            "correct_answer": q.correct_answer,
            "image_path": q.image_path
        })
    return result


@quiz_router.post("/submit")
def submit_answers(
    payload: SubmitPayload,
    user_id: str = Depends(check_jwt_token),
    service: IQuizService = Depends(get_quiz_service)
):
    if payload.genre_slug not in GENRE_SLUG_TO_ID:
        raise HTTPException(status_code=404, detail="Genre inconnu")

    from domain.models.quiz import QuizAnswer
    answers = [
        QuizAnswer(
            question_id=a.question_id,
            answer=a.answer,
            time_taken=a.time_taken
        )
        for a in payload.answers
    ]

    result = service.submit_answers(str(user_id), payload.genre_slug, answers)
    return {
        "total_points": result.total_points,
        "correct_count": result.correct_count,
        "new_global_score": result.new_global_score,
        "new_genre_score": result.new_genre_score,
        "global_level": result.global_level,
        "question_results": [
            {
                "question_id": r.question_id,
                "correct": r.correct,
                "points_earned": r.points_earned,
                "correct_answer": r.correct_answer
            }
            for r in result.question_results
        ]
    }


@quiz_router.get("/leaderboard")
def get_leaderboard(
    user_id: str = Depends(check_jwt_token),
    service: IQuizService = Depends(get_quiz_service)
):
    entries = service.get_leaderboard()
    return [
        {
            "rank": e.rank,
            "user_id": e.user_id,
            "username": e.username,
            "picture": e.picture,
            "total_score": e.total_score,
            "level": e.level
        }
        for e in entries
    ]


@quiz_router.get("/scores")
def get_user_scores(
    user_id: str = Depends(check_jwt_token),
    service: IQuizService = Depends(get_quiz_service)
):
    scores = service.get_user_scores(str(user_id))
    return {
        "global_score": scores.global_score,
        "global_level": scores.global_level,
        "genre_scores": [
            {
                "genre_slug": g.genre_slug,
                "total_score": g.total_score,
                "games_played": g.games_played
            }
            for g in scores.genre_scores
        ]
    }


def _shuffle_with_images(
    correct: str,
    wrong: list[str],
    question_type: str
) -> tuple[list[str], Optional[list[Optional[str]]]]:
    answers = wrong + [correct]
    random.shuffle(answers)

    if question_type != "poster_guess":
        return answers, None

    poster_map = _fetch_poster_paths(answers)
    images = [poster_map.get(title) for title in answers]
    return answers, images


def _fetch_poster_paths(titles: list[str]) -> dict[str, Optional[str]]:
    return QuizRepository().get_poster_paths(titles)
