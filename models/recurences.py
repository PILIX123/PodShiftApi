from pydantic import BaseModel
from datetime import time


class Reccurences(BaseModel):
    time: time


class EveryXDays(Reccurences):
    days: int


class EveryXMonths(Reccurences):
    months: int


class EveryNthofMonth(Reccurences):
    day: int
