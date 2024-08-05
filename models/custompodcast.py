from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid1
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from podcast import Podcast


class CustomPodcastBase(SQLModel):
    dateToPostAt: str
    podcast_id: int | None = Field(foreign_key="podcast.id")
    freq: int
    interval: int
    amount: int


class CustomPodcast(CustomPodcastBase, table=True):
    UUID: str = Field(default=str(uuid1()), primary_key=True)
    podcast: "Podcast" = Relationship(back_populates="customPodcasts")
