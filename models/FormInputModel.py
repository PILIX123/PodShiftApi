from pydantic import BaseModel
from models.recurences import EveryNthofMonth, EveryXDays, EveryXMonths


class FormInputModel(BaseModel):
    url: str
    recurrence: list[EveryNthofMonth | EveryXDays | EveryXMonths]
