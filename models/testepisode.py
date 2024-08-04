from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tespodcast import TestPodcast


class BaseTestEpisode(SQLModel):
    xml: str
    podcast_id: int | None = Field(foreign_key="testpodcast.id")


class TestEpisode(BaseTestEpisode, table=True):
    id: int = Field(default=None, primary_key=True)
    podcast: "TestPodcast" = Relationship(back_populates="episodes")
