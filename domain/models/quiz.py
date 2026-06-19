from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class QuizQuestion:
    id: int
    genre_slug: str
    question_type: str
    question_text: str
    correct_answer: str
    wrong_answers: list[str]
    image_path: Optional[str]


@dataclass(frozen=True)
class QuizAnswer:
    question_id: int
    answer: str
    time_taken: float


@dataclass(frozen=True)
class QuizQuestionResult:
    question_id: int
    correct: bool
    points_earned: int
    correct_answer: str


@dataclass(frozen=True)
class QuizResult:
    total_points: int
    correct_count: int
    new_global_score: int
    new_genre_score: int
    global_level: int
    question_results: list[QuizQuestionResult]


@dataclass(frozen=True)
class LeaderboardEntry:
    rank: int
    user_id: str
    username: str
    picture: Optional[str]
    total_score: int
    level: int


@dataclass(frozen=True)
class GenreScore:
    genre_slug: str
    total_score: int
    games_played: int


@dataclass(frozen=True)
class UserScores:
    global_score: int
    global_level: int
    genre_scores: list[GenreScore]
