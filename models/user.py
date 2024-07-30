from sqlmodel import SQLModel, Field
from typing import Any
from uuid import UUID


class UserBase(SQLModel):
    identification: str


class User(UserBase, table=True):
    guid: UUID = Field(default=None, primary_key=True)
