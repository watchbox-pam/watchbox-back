from typing import Optional
import datetime
import uuid

from sqlalchemy import ARRAY, BigInteger, Boolean, Column, Date, DateTime, Double, ForeignKeyConstraint, Identity, Integer, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, Uuid, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from database.db import Base
    
class Country(Base):
    __tablename__ = 'country'
    __table_args__ = (
        PrimaryKeyConstraint('iso', name='country_pkey'),
        UniqueConstraint('name', name='country_name_key')
    )

    iso: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    user: Mapped[list['User']] = relationship('User', back_populates='country_')


class CreditType(Base):
    __tablename__ = 'credit_type'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='credit_type_pkey'),
        UniqueConstraint('name', name='credit_type_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


class Department(Base):
    __tablename__ = 'department'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='department_pkey'),
        UniqueConstraint('name', name='department_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    job: Mapped[list['Job']] = relationship('Job', back_populates='department')


class Gender(Base):
    __tablename__ = 'gender'
    __table_args__ = (
        PrimaryKeyConstraint('value', name='gender_pkey'),
        UniqueConstraint('gender', name='gender_gender_key')
    )

    value: Mapped[int] = mapped_column(Integer, primary_key=True)
    gender: Mapped[str] = mapped_column(String, nullable=False)

    person: Mapped[list['Person']] = relationship('Person', back_populates='gender_')


class Keyword(Base):
    __tablename__ = 'keyword'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='keyword_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


class Language(Base):
    __tablename__ = 'language'
    __table_args__ = (
        PrimaryKeyConstraint('iso', name='language_pkey'),
    )

    iso: Mapped[str] = mapped_column(String, primary_key=True)
    english_name: Mapped[Optional[str]] = mapped_column(String)
    name: Mapped[Optional[str]] = mapped_column(String)


class MediaProvider(Base):
    __tablename__ = 'media_provider'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='media_provider_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    logo: Mapped[Optional[str]] = mapped_column(String)


class Movie(Base):
    __tablename__ = 'movie'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='movie_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    adult: Mapped[Optional[bool]] = mapped_column(Boolean)
    backdrop_path: Mapped[Optional[str]] = mapped_column(String)
    budget: Mapped[Optional[int]] = mapped_column(Integer)
    homepage: Mapped[Optional[str]] = mapped_column(Text)
    imdb_id: Mapped[Optional[str]] = mapped_column(String)
    original_language: Mapped[Optional[str]] = mapped_column(String)
    original_title: Mapped[Optional[str]] = mapped_column(String)
    overview: Mapped[Optional[str]] = mapped_column(Text)
    poster_path: Mapped[Optional[str]] = mapped_column(Text)
    release_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    revenue: Mapped[Optional[int]] = mapped_column(BigInteger)
    runtime: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[Optional[str]] = mapped_column(String)
    tagline: Mapped[Optional[str]] = mapped_column(Text)
    title: Mapped[Optional[str]] = mapped_column(String)
    popularity: Mapped[Optional[float]] = mapped_column(Double(53))
    video: Mapped[Optional[str]] = mapped_column(String)

    genre: Mapped[list['MovieGenre']] = relationship('MovieGenre', secondary='movie_movie_genre', back_populates='movie')
    comment: Mapped[list['Comment']] = relationship('Comment', back_populates='movie')
    playlist_media: Mapped[list['PlaylistMedia']] = relationship('PlaylistMedia', back_populates='movie')


class MovieGenre(Base):
    __tablename__ = 'movie_genre'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='movie_genre_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    movie: Mapped[list['Movie']] = relationship('Movie', secondary='movie_movie_genre', back_populates='genre')


class ProductionCompany(Base):
    __tablename__ = 'production_company'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='production_company_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    logo_path: Mapped[Optional[str]] = mapped_column(Text)
    name: Mapped[Optional[str]] = mapped_column(String)
    origin_country: Mapped[Optional[str]] = mapped_column(String)


class Tv(Base):
    __tablename__ = 'tv'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tv_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    adult: Mapped[Optional[bool]] = mapped_column(Boolean)
    backdrop_path: Mapped[Optional[str]] = mapped_column(String)
    episode_run_time: Mapped[Optional[list[int]]] = mapped_column(ARRAY(Integer()))
    first_air_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    homepage: Mapped[Optional[str]] = mapped_column(Text)
    in_production: Mapped[Optional[bool]] = mapped_column(Boolean)
    languages: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String()))
    last_air_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    name: Mapped[Optional[str]] = mapped_column(String)
    number_of_episodes: Mapped[Optional[int]] = mapped_column(Integer)
    number_of_seasons: Mapped[Optional[int]] = mapped_column(Integer)
    origin_country: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String()))
    original_language: Mapped[Optional[str]] = mapped_column(String)
    original_name: Mapped[Optional[str]] = mapped_column(String)
    overview: Mapped[Optional[str]] = mapped_column(Text)
    poster_path: Mapped[Optional[str]] = mapped_column(Text)
    release_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    revenue: Mapped[Optional[int]] = mapped_column(Integer)
    runtime: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[Optional[str]] = mapped_column(String)
    tagline: Mapped[Optional[str]] = mapped_column(Text)
    title: Mapped[Optional[str]] = mapped_column(String)
    video: Mapped[Optional[bool]] = mapped_column(Boolean)

    genre: Mapped[list['TvGenre']] = relationship('TvGenre', secondary='tv_tv_genre', back_populates='tv')
    person: Mapped[list['Person']] = relationship('Person', secondary='tv_created_by', back_populates='tv')
    tv_season: Mapped[list['TvSeason']] = relationship('TvSeason', back_populates='tv')
    comment: Mapped[list['Comment']] = relationship('Comment', back_populates='tv')
    playlist_media: Mapped[list['PlaylistMedia']] = relationship('PlaylistMedia', back_populates='tv')


class TvGenre(Base):
    __tablename__ = 'tv_genre'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tv_genre_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    tv: Mapped[list['Tv']] = relationship('Tv', secondary='tv_tv_genre', back_populates='genre')


class Job(Base):
    __tablename__ = 'job'
    __table_args__ = (
        ForeignKeyConstraint(['department_id'], ['department.id'], name='job_department_id_fkey'),
        PrimaryKeyConstraint('id', name='job_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    department_id: Mapped[Optional[int]] = mapped_column(Integer)

    department: Mapped[Optional['Department']] = relationship('Department', back_populates='job')


t_media_keyword = Table(
    'media_keyword', Base.metadata,
    Column('keyword_id', Integer, nullable=False),
    Column('movie_id', Integer),
    Column('tv_id', Integer),
    ForeignKeyConstraint(['keyword_id'], ['keyword.id'], name='media_keyword_keyword_id_fkey'),
    ForeignKeyConstraint(['movie_id'], ['movie.id'], name='media_keyword_movie_id_fkey'),
    ForeignKeyConstraint(['tv_id'], ['tv.id'], name='media_keyword_tv_id_fkey')
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


class Person(Base):
    __tablename__ = 'person'
    __table_args__ = (
        ForeignKeyConstraint(['gender'], ['gender.value'], name='person_gender_fkey'),
        PrimaryKeyConstraint('id', name='person_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    adult: Mapped[Optional[bool]] = mapped_column(Boolean)
    also_known_as: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String()))
    biography: Mapped[Optional[str]] = mapped_column(Text)
    birthday: Mapped[Optional[datetime.date]] = mapped_column(Date)
    deathday: Mapped[Optional[datetime.date]] = mapped_column(Date)
    gender: Mapped[Optional[int]] = mapped_column(Integer)
    homepage: Mapped[Optional[str]] = mapped_column(Text)
    imdb_id: Mapped[Optional[str]] = mapped_column(String)
    known_for_department: Mapped[Optional[str]] = mapped_column(String)
    name: Mapped[Optional[str]] = mapped_column(String)
    place_of_birth: Mapped[Optional[str]] = mapped_column(String)
    profile_path: Mapped[Optional[str]] = mapped_column(String)

    gender_: Mapped[Optional['Gender']] = relationship('Gender', back_populates='person')
    tv: Mapped[list['Tv']] = relationship('Tv', secondary='tv_created_by', back_populates='person')


class TvSeason(Base):
    __tablename__ = 'tv_season'
    __table_args__ = (
        ForeignKeyConstraint(['tv_id'], ['tv.id'], name='tv_season_tv_id_fkey'),
        PrimaryKeyConstraint('id', name='tv_season_pkey')
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    air_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    name: Mapped[Optional[str]] = mapped_column(String)
    overview: Mapped[Optional[str]] = mapped_column(Text)
    poster_path: Mapped[Optional[str]] = mapped_column(String)
    season_number: Mapped[Optional[int]] = mapped_column(Integer)
    tv_id: Mapped[Optional[int]] = mapped_column(Integer)

    tv: Mapped[Optional['Tv']] = relationship('Tv', back_populates='tv_season')
    tv_episode: Mapped[list['TvEpisode']] = relationship('TvEpisode', back_populates='season')


t_tv_tv_genre = Table(
    'tv_tv_genre', Base.metadata,
    Column('tv_id', Integer, primary_key=True),
    Column('genre_id', Integer, primary_key=True),
    ForeignKeyConstraint(['genre_id'], ['tv_genre.id'], name='tv_tv_genre_genre_id_fkey'),
    ForeignKeyConstraint(['tv_id'], ['tv.id'], name='tv_tv_genre_tv_id_fkey'),
    PrimaryKeyConstraint('tv_id', 'genre_id', name='tv_tv_genre_pkey')
)


class User(Base):
    __tablename__ = 'user'
    __table_args__ = (
        ForeignKeyConstraint(['country'], ['country.iso'], name='user_country_fkey'),
        PrimaryKeyConstraint('id', name='user_pkey'),
        UniqueConstraint('email', name='user_email_key'),
        UniqueConstraint('username', name='user_username_key')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    birthdate: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    history_private: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    adult_content: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    last_connection: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    salt: Mapped[str] = mapped_column(String(32), nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String)
    profile_picture_path: Mapped[Optional[str]] = mapped_column(String(256), comment="Chemin vers l'image de profil de l'utilisateur")
    banner_path: Mapped[Optional[str]] = mapped_column(String(256), comment="Chemin vers la bannière de l'utilisateur")
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    password_reset_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    verification_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    verification_code_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    country_: Mapped[Optional['Country']] = relationship('Country', back_populates='user')
    playlist: Mapped[list['Playlist']] = relationship('Playlist', back_populates='user')
    comment: Mapped[list['Comment']] = relationship('Comment', back_populates='user')


t_friend = Table(
    'friend', Base.metadata,
    Column('sender_id', Uuid, nullable=False),
    Column('receiver_id', Uuid, nullable=False),
    Column('is_pending', Boolean, nullable=False),
    Column('sent_at', DateTime, nullable=False),
    ForeignKeyConstraint(['receiver_id'], ['user.id'], name='friend_receiver_id_fkey'),
    ForeignKeyConstraint(['sender_id'], ['user.id'], name='friend_sender_id_fkey')
)


class Playlist(Base):
    __tablename__ = 'playlist'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['user.id'], name='playlist_user_id_fkey'),
        PrimaryKeyConstraint('id', name='playlist_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'))

    user: Mapped['User'] = relationship('User', back_populates='playlist')


t_tv_created_by = Table(
    'tv_created_by', Base.metadata,
    Column('tv_id', Integer, primary_key=True),
    Column('person_id', Integer, primary_key=True),
    ForeignKeyConstraint(['person_id'], ['person.id'], name='tv_created_by_person_id_fkey'),
    ForeignKeyConstraint(['tv_id'], ['tv.id'], name='tv_created_by_tv_id_fkey'),
    PrimaryKeyConstraint('tv_id', 'person_id', name='tv_created_by_pkey')
)


class TvEpisode(Base):
    __tablename__ = 'tv_episode'
    __table_args__ = (
        ForeignKeyConstraint(['season_id'], ['tv_season.id'], name='tv_episode_season_id_fkey'),
        PrimaryKeyConstraint('id', name='tv_episode_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    air_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    episode_number: Mapped[Optional[int]] = mapped_column(Integer)
    name: Mapped[Optional[str]] = mapped_column(String)
    overview: Mapped[Optional[str]] = mapped_column(Text)
    production_code: Mapped[Optional[str]] = mapped_column(String)
    runtime: Mapped[Optional[int]] = mapped_column(Integer)
    still_path: Mapped[Optional[str]] = mapped_column(String)
    season_id: Mapped[Optional[str]] = mapped_column(String)

    season: Mapped[Optional['TvSeason']] = relationship('TvSeason', back_populates='tv_episode')
    comment: Mapped[list['Comment']] = relationship('Comment', back_populates='tv_episode')


class Comment(Base):
    __tablename__ = 'comment'
    __table_args__ = (
        ForeignKeyConstraint(['movie_id'], ['movie.id'], name='comment_movie_id_fkey'),
        ForeignKeyConstraint(['tv_episode_id'], ['tv_episode.id'], name='comment_tv_episode_id_fkey'),
        ForeignKeyConstraint(['tv_id'], ['tv.id'], name='comment_tv_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['user.id'], name='comment_user_id_fkey'),
        PrimaryKeyConstraint('id', name='comment_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, comment='Contenu du commentaire')
    has_spoiler_warning: Mapped[bool] = mapped_column(Boolean, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    movie_id: Mapped[Optional[int]] = mapped_column(Integer)
    tv_id: Mapped[Optional[int]] = mapped_column(Integer)
    tv_episode_id: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'))

    movie: Mapped[Optional['Movie']] = relationship('Movie', back_populates='comment')
    tv_episode: Mapped[Optional['TvEpisode']] = relationship('TvEpisode', back_populates='comment')
    tv: Mapped[Optional['Tv']] = relationship('Tv', back_populates='comment')
    user: Mapped['User'] = relationship('User', back_populates='comment')


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


class PlaylistMedia(Playlist):
    __tablename__ = 'playlist_media'
    __table_args__ = (
        ForeignKeyConstraint(['movie_id'], ['movie.id'], name='playlist_media_movie_id_fkey'),
        ForeignKeyConstraint(['playlist_id'], ['playlist.id'], name='playlist_media_playlist_id_fkey'),
        ForeignKeyConstraint(['tv_id'], ['tv.id'], name='playlist_media_tv_id_fkey'),
        PrimaryKeyConstraint('playlist_id', name='playlist_media_pkey')
    )

    playlist_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    movie_id: Mapped[Optional[int]] = mapped_column(Integer)
    tv_id: Mapped[Optional[int]] = mapped_column(Integer)
    add_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'))

    movie: Mapped[Optional['Movie']] = relationship('Movie', back_populates='playlist_media')
    tv: Mapped[Optional['Tv']] = relationship('Tv', back_populates='playlist_media')
