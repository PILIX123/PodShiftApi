from pydantic import BaseModel
from models.forminputmodel import ReccurenceEnum


class FormUpdateModel(BaseModel):
    currentEpisode: int
    amountOfEpisode: int | None
    recurrence: ReccurenceEnum | None
    everyX: int | None
