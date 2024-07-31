from sqlmodel import Field, SQLModel, Relationship
from typing import List, TYPE_CHECKING
from uuid import uuid1

if TYPE_CHECKING:
    from podcast import Podcast


class CustomPodcastBase(SQLModel):
    dateToPostAt: str
    podcast_id: int | None = Field(foreign_key="podcast.id")


class CustomPodcast(CustomPodcastBase, table=True):
    # id: int = Field(default=None, primary_key=True)
    UUID: str = Field(default=str(uuid1()), primary_key=True)
    podcast: "Podcast" = Relationship(back_populates="customPodcasts")
