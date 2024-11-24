from pydantic import BaseModel


class ResponseModel(BaseModel):
    url: str


class PodcastResponseModel(BaseModel):
    UUID: str
    freq: int
    interval: int
    amount: int
    url: str
    title: str
