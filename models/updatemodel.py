from pydantic import BaseModel
from models.forminputmodel import ReccurenceEnum


class FormUpdateModel(BaseModel):
    currentEpisode: int
    amountOfEpisode: int
    recurrence: ReccurenceEnum
    everyX: int
