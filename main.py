from fastapi import FastAPI
from models.forminputmodel import FormInputModel
from pyPodcastParser.Podcast import Podcast
from requests import get

app = FastAPI(debug=__debug__)


@app.get('/')
async def root():
    return {"message": "Hello World"}


@app.post('/PodShift')
async def addFeed(form: FormInputModel):
    form.recurrence
    t = Podcast(get(form.url).content)
    t.items
    return {"message": f"{type(form.recurrence[0])}"}


@app.get("/PodShift/{userID}/{podcastID}")
async def getCustomFeed(userID, podcastID):
    pass
