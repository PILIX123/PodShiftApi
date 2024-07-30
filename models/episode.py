# episode.py
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from podcast import Podcast


class EpisodeBase(SQLModel):
    author: str | None
    comments: str | None
    creative_commons: str | None
    description: str | None
    enclosure_url: str | None
    enclosure_type: str | None
    enclosure_length: int | None
    itunes_author_name: str | None
    itunes_block: bool | None
    itunes_closed_captioned: str | None
    itunes_duration: str | None
    itunes_explicit: str | None
    itune_image: str | None
    itunes_order: str | None
    itunes_subtitle: str | None
    itunes_summary: str | None
    link: str | None
    published_date: str | None
    title: str | None
    date_time: datetime | None
    podcast_id: int = Field(foreign_key="podcast.id")


class Episode(EpisodeBase, table=True):
    id: int = Field(default=None, primary_key=True)
    podcast: "Podcast" = Relationship(back_populates="episodes")
