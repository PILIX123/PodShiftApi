from sqlmodel import Field, SQLModel
import typing
from datetime import datetime
from time import time


class Episode(SQLModel, table=True):
    guid: str = Field(default=None, primary_key=True)
    pudDate: datetime
    title: str
    itunes_title: str
    itunes_episode: int
    itunes_author: str
    itunes_duration: time
