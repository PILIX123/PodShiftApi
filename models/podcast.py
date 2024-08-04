from sqlmodel import Field, SQLModel, Relationship
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from episode import Episode
    from custompodcast import CustomPodcast


class BasePodacast(SQLModel):
    xml: str = Field(default=None, unique=True)
    url: str


class Podcast(BasePodacast, table=True):
    id: int = Field(default=None, primary_key=True)
    episodes: List["Episode"] = Relationship(back_populates="podcast")
    customPodcasts: List["CustomPodcast"] = Relationship(
        back_populates="podcast")
