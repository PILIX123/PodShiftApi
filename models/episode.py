from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from podcast import Podcast


class BaseEpisode(SQLModel):
    xml: str
    podcast_id: int | None = Field(foreign_key="podcast.id")


class Episode(BaseEpisode, table=True):
    id: int = Field(default=None, primary_key=True)
    podcast: "Podcast" = Relationship(back_populates="episodes")
