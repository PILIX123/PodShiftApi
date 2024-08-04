from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid1
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tespodcast import TestPodcast


class TestCustomPodcastBase(SQLModel):
    dateToPostAt: str
    podcast_id: int | None = Field(foreign_key="testpodcast.id")


class TestCustomPodcast(TestCustomPodcastBase, table=True):
    # id: int = Field(default=None, primary_key=True)
    UUID: str = Field(default=str(uuid1()), primary_key=True)
    podcast: "TestPodcast" = Relationship(back_populates="customPodcasts")
