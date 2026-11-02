from typing import Optional, List

from domain.interfaces.repositories.i_movie_repository import IMovieRepository
from domain.models.movie import PopularMovieList, MovieDetail
from domain.models.movie_list_item import MovieListItem
from utils.tmdb_service import call_tmdb_api
from database.db import SessionLocal
from database.models import Movie as DBMovie, MovieGenre, t_movie_movie_genre
from datetime import date
from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload
from utils.background_save import save_in_background

import logging
logger = logging.getLogger(__name__)

def _parse_date(s: str | None) -> date | None:
    try:
        return date.fromisoformat(s) if s else None
    except ValueError:
        return None

class MovieRepository(IMovieRepository):
    def find_by_id(self, movie_id: int, include_adult: bool) -> Optional[MovieDetail]:
        row = self._get_complete(movie_id)
        if row:
            if row.adult and not include_adult:
                return None
            return self._row_to_detail(row)

        result = call_tmdb_api(f"/movie/{movie_id}?language=fr-FR")
        if not result or "id" not in result:
            logger.warning("TMDB sans résultat pour le film %s : %s", movie_id, result)
            return None
        save_in_background(("movie", result["id"]), self._save, result)

        if not include_adult and result.get("adult"):
            return None

        movie = MovieDetail(
            id=result["id"],
            adult=result["adult"],
            backdrop_path=result["backdrop_path"],
            budget=result["budget"],
            genres=result["genres"],
            original_language=result["original_language"],
            original_title=result["original_title"],
            overview=result["overview"],
            poster_path=result["poster_path"],
            release_date=result["release_date"],
            revenue=result["revenue"],
            runtime=result["runtime"],
            status=result["status"],
            title=result["title"],
            video=result["video"],
            infos_complete=True
        )
        return movie

    def _get_complete(self, movie_id: int):
        with SessionLocal() as session:
            return session.scalars(
                select(DBMovie)
                .where(DBMovie.id == movie_id, DBMovie.infos_complete.is_(True))
                .options(selectinload(DBMovie.genre))
            ).first()

    def _row_to_detail(self, row) -> MovieDetail:
        return MovieDetail(
            id=row.id,
            adult=row.adult,
            backdrop_path=row.backdrop_path,
            budget=row.budget,
            genres=[{"id": g.id, "name": g.name} for g in row.genre],
            original_language=row.original_language,
            original_title=row.original_title,
            overview=row.overview,
            poster_path=row.poster_path,
            release_date=row.release_date.isoformat() if row.release_date else "",
            revenue=row.revenue,
            runtime=row.runtime,
            status=row.status,
            title=row.title,
            video=row.video,
            infos_complete=True
        )

    def _save(self, data: dict) -> None:
        values = dict(
            id=data["id"],
            adult=data.get("adult"),
            backdrop_path=data.get("backdrop_path"),
            budget=data.get("budget"),
            homepage=data.get("homepage"),
            imdb_id=data.get("imdb_id"),
            original_language=data.get("original_language"),
            original_title=data.get("original_title"),
            overview=data.get("overview"),
            poster_path=data.get("poster_path"),
            release_date=_parse_date(data.get("release_date")),
            revenue=data.get("revenue"),
            runtime=data.get("runtime"),
            status=data.get("status"),
            tagline=data.get("tagline"),
            title=data.get("title"),
            popularity=data.get("popularity"),
            video=bool(data.get("video")),
            infos_complete=True
        )
        genres = data.get("genres") or []

        with SessionLocal() as session, session.begin():
            session.execute(
                insert(DBMovie)
                .values(**values)
                .on_conflict_do_update(
                    index_elements=["id"],
                    set_={k: v for k, v in values.items() if k != "id"},
                )
            )
            if genres:
                session.execute(
                    insert(MovieGenre)
                    .values([{"id": g["id"], "name": g["name"]} for g in genres])
                    .on_conflict_do_nothing()
                )
            session.execute(delete(t_movie_movie_genre)
                            .where(t_movie_movie_genre.c.movie_id == data["id"]))

            if genres:
                session.execute(insert(t_movie_movie_genre)
                    .values([{"movie_id": data["id"], "genre_id": g["id"]} for g in genres]))

    def search(self, search_term: str, include_adult: bool) -> Optional[list[MovieDetail]]:
        adult_str = "true" if include_adult else "false"
        endpoint = f"/search/movie?query={search_term}&include_adult={adult_str}&language=fr-FR"

        result = call_tmdb_api(endpoint)

        movies: list[MovieDetail] = []

        for res in result["results"]:
            movies.append(MovieDetail(
                id=res["id"],
                adult=res["adult"],
                backdrop_path=res["backdrop_path"],
                budget=0,
                genres=[],
                original_language=res["original_language"],
                original_title=res["original_title"],
                overview=res["overview"],
                poster_path=res["poster_path"],
                release_date=res["release_date"],
                revenue=0,
                runtime=0,
                status="",
                title=res["title"],
                video=res["video"],
                infos_complete=True
            ))

        return movies

    def find_by_time_window(self, time_window: str, page: int, include_adult: bool) -> Optional[PopularMovieList]:
        endpoint = f"/trending/movie/{time_window}?page={page}&language=fr-FR"

        result = call_tmdb_api(endpoint)

        results = result["results"] if include_adult else [r for r in result["results"] if not r.get("adult")]

        movies = PopularMovieList(
            page=result["page"],
            results=results,
            total_results=result["total_pages"],
            total_pages=result["total_results"]
        )

        return movies

    def find_by_genre(self, genre: str, include_adult: bool) -> Optional[PopularMovieList]:
        adult_str = "true" if include_adult else "false"
        endpoint = f"/discover/movie?with_genres={genre}&include_adult={adult_str}&include_video=false&language=fr-FR&page=1&sort_by=popularity.desc"

        result = call_tmdb_api(endpoint)

        movies = PopularMovieList(
            page=result["page"],
            results=result["results"],
            total_results=result["total_pages"],
            total_pages=result["total_results"]
        )

        return movies

    def movie_runtime(self, movie_ids: List[int]) -> int:
        try:
            with SessionLocal() as session:
                movies = session.query(DBMovie).filter(DBMovie.id.in_(movie_ids))
                total_runtime = sum(movie.runtime or 0 for movie in movies)
                return total_runtime
        except Exception as e:
            print(f"[ERREUR] Exception dans movie_runtime : {e}")
            return 0

    def get_random_movies(self, count: int = 50, include_adult: bool = False) -> Optional[List[MovieListItem]]:

        movies: List[DBMovie] = []

        try:
            with SessionLocal() as session:
                query = session.query(DBMovie).filter(DBMovie.popularity >= 70)
                if not include_adult:
                    query = query.filter((DBMovie.adult == False) | (DBMovie.adult == None))
                results = query.order_by(func.random()).limit(count).all()
                for result in results:
                    movies.append(MovieListItem(
                        id=result.id,
                        title=result.title,
                        poster_path=result.poster_path
                    ))

        except Exception as e:
            print(e)

        return movies
