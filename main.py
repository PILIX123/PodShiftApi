from fastapi import FastAPI
from models.forminputmodel import FormInputModel
from pyPodcastParser.Podcast import Podcast
from requests import get
from utils.parser import create_rrule_from_dates


app = FastAPI(debug=__debug__)


@app.get('/')
async def root():
    return {"message": "Hello World"}


@app.post('/PodShift')
async def addFeed(form: FormInputModel):
    test = create_rrule_from_dates(form.recurrence)
    return {"message": f"{list(test)}"}


@app.get("/PodShift/{userID}/{podcastID}")
async def getCustomFeed(userID, podcastID):
    pass
