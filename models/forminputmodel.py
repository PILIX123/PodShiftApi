from pydantic import BaseModel
from enum import IntEnum
from dateutil.rrule import WEEKLY, DAILY, MONTHLY, YEARLY


class ReccurenceEnum(IntEnum):
    WEEKLY = (WEEKLY,)  # 2
    DAILY = (DAILY,)  # 3
    MONTHLY = (MONTHLY,)  # 1
    YEARLY = YEARLY  # 0


class FormInputModel(BaseModel):
    url: str
    amountOfEpisode: int = 1
    recurrence: ReccurenceEnum
    everyX: int = 1
