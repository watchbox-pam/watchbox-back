from sqlalchemy import ForeignKeyConstraint, Integer, String, Table, Column, PrimaryKeyConstraint, Uuid, Boolean, DateTime, Text, Identity, text
from database.models.base import Base

t_media_keyword = Table(
    'media_keyword', Base.metadata,
    Column('keyword_id', Integer, nullable=False),
    Column('movie_id', Integer),
    Column('tv_id', Integer),
    ForeignKeyConstraint(['keyword_id'], ['keyword.id'], name='media_keyword_keyword_id_fkey'),
    ForeignKeyConstraint(['movie_id'], ['movie.id'], name='media_keyword_movie_id_fkey')
)

t_media_language = Table(
    'media_language', Base.metadata,
    Column('movie_id', Integer),
    Column('tv_id', Integer),
    Column('language_id', String),
    ForeignKeyConstraint(['language_id'], ['language.iso'], name='media_language_language_id_fkey'),
    ForeignKeyConstraint(['movie_id'], ['movie.id'], name='media_language_movie_id_fkey'),
    ForeignKeyConstraint(['tv_id'], ['tv.id'], name='media_language_tv_id_fkey')
)

t_media_media_provider = Table(
    'media_media_provider', Base.metadata,
    Column('movie_id', Integer),
    Column('tv_id', Integer),
    Column('media_provider_id', Integer, nullable=False),
    Column('country', String, nullable=False),
    ForeignKeyConstraint(['country'], ['country.iso'], name='media_media_provider_country_fkey'),
    ForeignKeyConstraint(['media_provider_id'], ['media_provider.id'], name='media_media_provider_media_provider_id_fkey'),
    ForeignKeyConstraint(['movie_id'], ['movie.id'], name='media_media_provider_movie_id_fkey'),
    ForeignKeyConstraint(['tv_id'], ['tv.id'], name='media_media_provider_tv_id_fkey')
)

t_media_production_company = Table(
    'media_production_company', Base.metadata,
    Column('tv_id', Integer),
    Column('movie_id', Integer),
    Column('company_id', Integer, nullable=False),
    ForeignKeyConstraint(['company_id'], ['production_company.id'], name='media_production_company_company_id_fkey'),
    ForeignKeyConstraint(['movie_id'], ['movie.id'], name='media_production_company_movie_id_fkey'),
    ForeignKeyConstraint(['tv_id'], ['tv.id'], name='media_production_company_tv_id_fkey')
)

t_media_production_country = Table(
    'media_production_country', Base.metadata,
    Column('country_id', String, nullable=False),
    Column('tv_id', Integer),
    Column('movie_id', Integer),
    ForeignKeyConstraint(['country_id'], ['country.iso'], name='media_production_country_country_id_fkey'),
    ForeignKeyConstraint(['movie_id'], ['movie.id'], name='media_production_country_movie_id_fkey'),
    ForeignKeyConstraint(['tv_id'], ['tv.id'], name='media_production_country_tv_id_fkey')
)

t_movie_movie_genre = Table(
    'movie_movie_genre', Base.metadata,
    Column('movie_id', Integer, primary_key=True),
    Column('genre_id', Integer, primary_key=True),
    ForeignKeyConstraint(['genre_id'], ['movie_genre.id'], name='movie_movie_genre_genre_id_fkey'),
    ForeignKeyConstraint(['movie_id'], ['movie.id'], name='movie_movie_genre_movie_id_fkey'),
    PrimaryKeyConstraint('movie_id', 'genre_id', name='movie_movie_genre_pkey')
)

t_tv_tv_genre = Table(
    'tv_tv_genre', Base.metadata,
    Column('tv_id', Integer, primary_key=True),
    Column('genre_id', Integer, primary_key=True),
    ForeignKeyConstraint(['genre_id'], ['tv_genre.id'], name='tv_tv_genre_genre_id_fkey'),
    ForeignKeyConstraint(['tv_id'], ['tv.id'], name='tv_tv_genre_tv_id_fkey'),
    PrimaryKeyConstraint('tv_id', 'genre_id', name='tv_tv_genre_pkey')
)

t_friend = Table(
    'friend', Base.metadata,
    Column('sender_id', Uuid, nullable=False),
    Column('receiver_id', Uuid, nullable=False),
    Column('is_pending', Boolean, nullable=False),
    Column('sent_at', DateTime, nullable=False),
    ForeignKeyConstraint(['receiver_id'], ['user.id'], name='friend_receiver_id_fkey'),
    ForeignKeyConstraint(['sender_id'], ['user.id'], name='friend_sender_id_fkey')
)

t_tv_created_by = Table(
    'tv_created_by', Base.metadata,
    Column('tv_id', Integer, primary_key=True),
    Column('person_id', Integer, primary_key=True),
    ForeignKeyConstraint(['person_id'], ['person.id'], name='tv_created_by_person_id_fkey'),
    ForeignKeyConstraint(['tv_id'], ['tv.id'], name='tv_created_by_tv_id_fkey'),
    PrimaryKeyConstraint('tv_id', 'person_id', name='tv_created_by_pkey')
)

t_credit = Table(
    'credit', Base.metadata,
    Column('tv_id', Integer),
    Column('tv_season_id', String),
    Column('tv_episode_id', Integer),
    Column('movie_id', Integer),
    Column('person_id', Integer, nullable=False),
    Column('type', Integer, nullable=False),
    Column('character', String),
    Column('order', Integer),
    Column('job_id', Integer),
    ForeignKeyConstraint(['job_id'], ['job.id'], name='credit_job_id_fkey'),
    ForeignKeyConstraint(['movie_id'], ['movie.id'], name='credit_movie_id_fkey'),
    ForeignKeyConstraint(['person_id'], ['person.id'], name='credit_person_id_fkey'),
    ForeignKeyConstraint(['tv_episode_id'], ['tv_episode.id'], name='credit_tv_episode_id_fkey'),
    ForeignKeyConstraint(['type'], ['credit_type.id'], name='credit_type_fkey')
)


t_playlist_media = Table(
    'playlist_media', Base.metadata,
    Column('playlist_id', Uuid, nullable=False),
    Column('movie_id', Integer),
    Column('tv_id', Integer),
    Column('add_date', DateTime, server_default=text('now()')),
    ForeignKeyConstraint(['movie_id'], ['movie.id'], name='playlist_media_movie_id_fkey'),
    ForeignKeyConstraint(['playlist_id'], ['playlist.id'], name='playlist_media_playlist_id_fkey', ondelete='CASCADE'),
    ForeignKeyConstraint(['tv_id'], ['tv.id'], name='playlist_media_tv_id_fkey')
)


t_review = Table(
    'review', Base.metadata,
    Column('rating', Integer, nullable=False),
    Column('comment', Text, comment='Contenu du commentaire'),
    Column('has_spoiler_warning', Boolean, nullable=False),
    Column('movie_id', Integer),
    Column('tv_id', Integer),
    Column('tv_episode_id', Integer),
    Column('user_id', Uuid, nullable=False),
    Column('created_at', DateTime, server_default=text('now()')),
    Column('id', Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), nullable=False),
    ForeignKeyConstraint(['movie_id'], ['movie.id'], name='comment_movie_id_fkey'),
    ForeignKeyConstraint(['tv_episode_id'], ['tv_episode.id'], name='comment_tv_episode_id_fkey'),
    ForeignKeyConstraint(['tv_id'], ['tv.id'], name='comment_tv_id_fkey'),
    ForeignKeyConstraint(['user_id'], ['user.id'], name='comment_user_id_fkey', ondelete='CASCADE'),
)


t_ml_training_counter = Table(
    'ml_training_counter', Base.metadata,
    Column('id', Integer, Identity(always=False, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), nullable=False),
    Column('new_ratings_count', Integer, server_default=text('0')),
    Column('last_trained_at', DateTime, server_default=text('now()')),
    PrimaryKeyConstraint('id', name='ml_training_counter_pkey')
)