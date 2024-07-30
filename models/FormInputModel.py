from pydantic import BaseModel
from typing import List

"""
    Front end will get the number of episodes and make the rrule and then transmit it to 
    the backend where the logic will be used to create all the data inside the database
"""


class FormInputModel(BaseModel):
    url: str
    recurrence: List[str]
