import typing
from sqlmodel import Field, SQLModel
from datetime import datetime
from models.episode import Episode


class Podcast(SQLModel, table=True):
    id: typing.Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    author: str
    subtitle: str
    link: str
    language: str
    lastBuildDate: datetime
    itunes_category: str
    image: str
    explicit: bool
    copyright: str
    # however the list are supposed to work in this one
    items: typing.List[Episode]
