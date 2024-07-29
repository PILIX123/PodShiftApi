from pydantic import BaseModel
from typing import List


class FormInputModel(BaseModel):
    url: str
    recurrence: List[str]
