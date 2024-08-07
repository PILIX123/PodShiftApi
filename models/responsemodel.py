from pydantic import BaseModel


class ResponseModel(BaseModel):
    url: str
