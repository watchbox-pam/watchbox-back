from typing import Optional, List

from domain.interfaces.repositories.i_movie_repository import IMovieRepository
from domain.models.movie import PopularMovieList, MovieDetail
from domain.models.genre import Genre
from domain.models.movieRecommendation import MovieRecommendation
from domain.models.movie_list_item import MovieListItem
from utils.tmdb_service import call_tmdb_api
from database.db import SessionLocal
from database.models.movie import Movie as DBMovie
from database.models.movie_translation import MovieTranslation as DBMovieTranslation
from database.models.movie_genre import MovieGenre as DBMovieGenre
from database.models.language import Language as DBLanguage
from sqlalchemy import func, select

class MovieRepository(IMovieRepository):
    def find_by_id(self, movie_id: int, include_adult: bool) -> Optional[MovieDetail]:
        try:
            print(include_adult)
            with SessionLocal() as session:
                existing_movie = session.query(DBMovie).filter(DBMovie.id == movie_id).first()
                
                if existing_movie is None:
                    print(f"[INFO] Movie with id {movie_id} not found in database, fetching from TMDB API")
                    endpoint = f"/movie/{movie_id}?language=fr-FR"

                    result = call_tmdb_api(endpoint)

                    genres = []
                    for genre in result.get("genres", []):
                        db_genre = session.query(DBMovieGenre).filter(DBMovieGenre.id == genre["id"]).first()
                        if db_genre is None:
                            db_genre = DBMovieGenre(
                                id=genre["id"],
                                name=genre["name"],
                                movie=[]
                            )
                            session.add(db_genre)
                        genres.append(db_genre)

                    translation_language = session.query(DBLanguage).filter(DBLanguage.iso == "fr").first()
                    if translation_language is None:
                        translation_language = DBLanguage(
                            iso="fr",
                            english_name="French",
                            name="Français",
                            movie_translations=[]
                        )
                        session.add(translation_language)

                    new_movie = DBMovie(
                        id=result["id"],
                        adult=result["adult"],
                        backdrop_path=result["backdrop_path"],
                        budget=result["budget"],
                        homepage=result.get("homepage"),
                        imdb_id=result.get("imdb_id"),
                        original_language=result["original_language"],
                        original_title=result["original_title"],
                        release_date=result["release_date"],
                        revenue=result["revenue"],
                        runtime=result["runtime"],
                        status=result["status"],
                        popularity=result.get("popularity"),
                        video=result["video"],
                        updated_at=func.now(),
                        translations=[
                            DBMovieTranslation(
                                id=None,
                                movie_id=result["id"],
                                language_iso=translation_language.iso,
                                overview=result.get("overview"),
                                poster_path=result.get("poster_path"),
                                tagline=result.get("tagline"),
                                title=result.get("title"),
                                updated_at=func.now(),
                                movie=None,
                                language=translation_language
                            )
                        ],
                        genre=genres
                    )

                    session.add(new_movie)
                    session.commit()

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
                        video=result["video"]
                    )

                    return movie
                
                else:
                    print(f"[INFO] Movie with id {movie_id} found in database, returning stored data")

                    translation = session.query(DBMovieTranslation).filter(
                        DBMovieTranslation.movie_id == movie_id,
                        DBMovieTranslation.language_iso == "fr"
                    ).first()
                    if translation is None:
                        print(f"[INFO] No French translation found for movie with id {movie_id}, returning data without translation")

                    genres = [Genre(id=genre.id, name=genre.name) for genre in existing_movie.genre]
                    return MovieDetail(
                        id=existing_movie.id,
                        adult=existing_movie.adult,
                        backdrop_path=existing_movie.backdrop_path,
                        budget=existing_movie.budget,
                        genres=genres,
                        original_language=existing_movie.original_language,
                        original_title=existing_movie.original_title,
                        overview=translation.overview if translation else "",
                        poster_path=translation.poster_path if translation else "",
                        release_date=existing_movie.release_date,
                        revenue=existing_movie.revenue,
                        runtime=existing_movie.runtime,
                        status=existing_movie.status,
                        title=translation.title if translation else existing_movie.original_title,
                        video=existing_movie.video,
                    )
                
                    # id=result["id"],
                    # adult=result["adult"],
                    # backdrop_path=result["backdrop_path"],
                    # budget=result["budget"],
                    # genres=result["genres"],
                    # original_language=result["original_language"],
                    # original_title=result["original_title"],
                    # overview=result["overview"],
                    # poster_path=result["poster_path"],
                    # release_date=result["release_date"],
                    # revenue=result["revenue"],
                    # runtime=result["runtime"],
                    # status=result["status"],
                    # title=result["title"],
                    # video=result["video"],
                    # infos_complete=True
                
        except Exception as e:
            print(f"[ERREUR] Exception dans find_by_id : {e}")
            return None


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
                total_runtime = sum(movie.runtime for movie in movies)
                return total_runtime
        except Exception as e:
            print(f"[ERREUR] Exception dans movie_runtime : {e}")
            return 0

    def get_random_movies(self, count: int = 50, include_adult: bool = False) -> Optional[List[MovieListItem]]:

        movies: List[DBMovie] = []

        try:
            with SessionLocal() as session:
                results = session.execute(
                    select(
                        DBMovie.id,
                        DBMovieTranslation.title,
                        DBMovieTranslation.poster_path
                    ).join(
                        DBMovieTranslation
                    ).where(
                        DBMovieTranslation.language_iso == "fr",
                        DBMovie.popularity >= 70,
                        (DBMovie.adult == False) | (DBMovie.adult == None) if not include_adult else True
                    ).order_by(
                        func.random()
                    ).limit(count)
                ).fetchall()

                for result in results:
                    movies.append(MovieListItem(
                        id=result.id,
                        title=result.title,
                        poster_path=result.poster_path
                    ))

        except Exception as e:
            print(e)

        return movies