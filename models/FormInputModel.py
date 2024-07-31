from pydantic import BaseModel
from enum import IntEnum
from dateutil.rrule import WEEKLY, DAILY, MONTHLY, YEARLY


class ReccurenceEnum(IntEnum):
    WEEKLY = WEEKLY,
    DAILY = DAILY,
    MONTHLY = MONTHLY,
    YEARLY = YEARLY


class FormInputModel(BaseModel):
    url: str
    recurrence: ReccurenceEnum
    everyX: int = 1
