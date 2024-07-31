from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from episode import Episode


class PodcastBase(SQLModel):
    copyright: str | None
    creative_commons: str | None
    description: str | None
    generator: str | None
    image_title: str | None
    image_url: str | None
    image_link: str | None
    image_width: str | None
    image_height: str | None
    itunes_author_name: str | None
    itunes_block: bool | None
    itunes_complete: str | None
    itunes_explicit: str | None
    itune_image: str | None
    itunes_new_feed_url: str | None
    language: str | None
    last_build_date: str | None
    link: str | None
    managing_editor: str | None
    published_date: str | None
    pubsubhubbub: str | None
    owner_name: str | None
    owner_email: str | None
    subtitle: str | None
    web_master: str | None
    date_time: datetime | None


class Podcast(PodcastBase, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(default=None, unique=True)
    episodes: List["Episode"] = Relationship(back_populates="podcast")
