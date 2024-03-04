from pydantic import BaseModel
from models.recurences import Reccurences, EveryNthofMonth, EveryXDays, EveryXMonths
from datetime import datetime


class FormInputModel(BaseModel):
    url: str
    recurrence: list[EveryNthofMonth | EveryXDays | EveryXMonths]
