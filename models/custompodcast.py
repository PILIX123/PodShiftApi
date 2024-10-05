from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from podcast import Podcast  # pragma: no cover


class CustomPodcastBase(SQLModel):
    dateToPostAt: str
    podcast_id: int | None = Field(foreign_key="podcast.id")
    freq: int
    interval: int
    amount: int = Field(default=1)


class CustomPodcast(CustomPodcastBase, table=True):
    UUID: str = Field(default=None, primary_key=True)
    podcast: "Podcast" = Relationship(back_populates="customPodcasts")
