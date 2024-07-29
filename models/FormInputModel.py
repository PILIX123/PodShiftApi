from pydantic import BaseModel
from typing import Any


class FormInputModel(BaseModel):
    url: str
    recurrence: Any
