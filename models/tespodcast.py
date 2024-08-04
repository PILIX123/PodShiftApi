from sqlmodel import Field, SQLModel, Relationship
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from testepisode import TestEpisode
    from testcutompodcast import TestCustomPodcast


class BaseTestPodacast(SQLModel):
    xml: str = Field(default=None, unique=True)
    url: str


class TestPodcast(BaseTestPodacast, table=True):
    id: int = Field(default=None, primary_key=True)
    episodes: List["TestEpisode"] = Relationship(back_populates="podcast")
    customPodcasts: List["TestCustomPodcast"] = Relationship(
        back_populates="podcast")
