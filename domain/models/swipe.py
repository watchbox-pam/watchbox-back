from pydantic import BaseModel


class SwipeRequest(BaseModel):
    movie_id: int
    direction: str  # 'like', 'dislike', 'skip'
