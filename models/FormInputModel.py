from pydantic import BaseModel
from datetime import datetime


class FormInputModel(BaseModel):
    url: str
