from pydantic import BaseModel


class ResponseModel(BaseModel):
    custom_url: str
    UUID: str
    title: str
    frequence: int
    interval: int
    amount: int
    url: str


class PodcastResponseModel(BaseModel):
    UUID: str
    freq: int
    interval: int
    amount: int
    url: str
    title: str
