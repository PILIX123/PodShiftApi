import os
from datetime import datetime
import json

from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from uvicorn.config import LOGGING_CONFIG
from requests import get
from dateutil.parser import parse
from sqlalchemy.exc import IntegrityError

from sqlmodel import Session
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from db import get_session, Database
from models.forminputmodel import FormInputModel
from models.responsemodel import ResponseModel
from utils.xml_reader import createPodcast, extractContents
from utils.util import dateListRRule
from cronjob import updateFeeds

ENVIRONEMENT_URL = "localhost:8000" if os.getenv(
    "DEBUG") else "podshift.ddns.net:8080"
LOGGING_CONFIG["formatters"]["access"]["fmt"] = "%(asctime)s " + \
    LOGGING_CONFIG["formatters"]["access"]["fmt"]

scheduler = BackgroundScheduler()
trigger = IntervalTrigger(seconds=2, start_date=datetime.now()) if os.getenv(
    "DEBUG") else IntervalTrigger(hours=2, start_date=datetime.now())
scheduler.add_job(updateFeeds, trigger)
scheduler.start()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    scheduler.shutdown()

app = FastAPI(title="PodShiftAPI", lifespan=lifespan)
db = Database()


@app.post('/PodShift')
async def addFeed(form: FormInputModel, session: Session = Depends(get_session)):
    podcastContent = get(form.url).content.decode()
    podcastXML, episodesXMLList = extractContents(podcastContent)

    try:
        podcast = db.createNewPodcast(
            podcastXML=podcastXML,
            podcastUrl=form.url,
            episodeListXML=episodesXMLList,
            session=session
        )
    except IntegrityError as e:
        db.rollback(session)
        if "UNIQUE" in e.args[0]:
            podcast = db.getPodcastXML(podcastXML, session)
        else:
            raise HTTPException(status_code=409, detail=f"{e.detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    listDate = dateListRRule(
        freq=form.recurrence,
        date=datetime.date(datetime.now()),
        interval=form.everyX,
        nbEpisodes=len(episodesXMLList),
        amount=form.amountOfEpisode
    )
    jsonDumps = json.dumps(listDate)
    customPodcast = db.createCustomPodcast(
        jsonDumpDate=jsonDumps,
        interval=form.everyX,
        freq=form.recurrence,
        podcast=podcast,
        amount=form.amountOfEpisode,
        session=session
    )
    return JSONResponse(content=jsonable_encoder(ResponseModel(url=f"http://{ENVIRONEMENT_URL}/PodShift/{customPodcast.UUID}")))


@app.get("/PodShift/{customPodcastGUID}")
async def getCustomFeed(customPodcastGUID, session: Session = Depends(get_session)):
    customFeed = db.getCustomPodcast(customPodcastGUID, session)

    content = createPodcast(
        podcastContent=customFeed.podcast.xml,
        parsedDates=[parse(d) for d in json.loads(customFeed.dateToPostAt)],
        amount=customFeed.amount,
        listEpisodes=[ep.xml for ep in customFeed.podcast.episodes]
    )

    return Response(content=content, media_type="application/xml")
