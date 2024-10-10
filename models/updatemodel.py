from pydantic import BaseModel
from models.forminputmodel import ReccurenceEnum


class FormUpdateModel(BaseModel):
    amountOfEpisode: int = 1
    recurrence: ReccurenceEnum
    everyX: int = 1
