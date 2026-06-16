from database.models.association_tables import (
	t_media_keyword,
	#t_media_language,
	t_media_media_provider,
	t_media_production_company,
	t_media_production_country,
	t_movie_movie_genre,
	t_tv_tv_genre,
	t_friend,
	t_tv_created_by,
	t_credit,
	t_playlist_media,
	t_review,
	t_ml_training_counter,
)
from database.models.base import Base
from database.models.country import Country
from database.models.credit_type import CreditType
from database.models.department import Department
from database.models.gender import Gender
from database.models.job import Job
from database.models.keyword import Keyword
from database.models.language import Language
from database.models.media_provider import MediaProvider
from database.models.movie_genre import MovieGenre
from database.models.movie import Movie
from database.models.person import Person
from database.models.playlist import Playlist
from database.models.production_company import ProductionCompany
from database.models.tv_episode import TvEpisode
from database.models.tv_genre import TvGenre
from database.models.tv_season import TvSeason
from database.models.tv import Tv
from database.models.user import User
from database.models.movie_translation import MovieTranslation