import os
from datetime import datetime
import json
from xml.etree import ElementTree as ET

from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from uvicorn.config import LOGGING_CONFIG
from requests import get
from dateutil.rrule import rrule
from dateutil.parser import parse
from sqlalchemy.exc import IntegrityError

from sqlmodel import Session, select
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from db import get_session, Database, createCustomPodcast
from models.forminputmodel import FormInputModel
from models.episode import Episode
from models.podcast import Podcast
from models.custompodcast import CustomPodcast
from models.responsemodel import ResponseModel
from utils.xml_reader import createPodcast, extractContents
from utils.util import dateListRRule


def updateFeeds():
    session = next(get_session())
    stmnt = select(Podcast)
    r = session.exec(stmnt)

    for podcast in r:
        print(podcast.url)
        feed = ET.fromstring(get(podcast.url).content.decode())
        channel = feed.find("channel")
        episodesFromFeed = [ET.tostring(item, encoding="unicode")
                            for item in channel.findall("item")]
        latestEpisode = ET.tostring(
            channel.find("item"), encoding='unicode')
        latestDbEpisode = podcast.episodes[-1]
        if latestEpisode == latestDbEpisode.xml:
            continue
        else:
            podcast.episodes.append(Episode(
                xml=latestEpisode, podcast=podcast))
            session.commit()
            for subcription in podcast.customPodcasts:
                dateToPostAt = json.loads(subcription.dateToPostAt)
                startFreq = dateToPostAt[0]
                newRrule = rrule(
                    freq=subcription.freq,
                    dtstart=parse(startFreq),
                    interval=subcription.interval,
                    count=len(podcast.episodes)/subcription.amount
                )
                subcription.dateToPostAt = json.dumps(
                    [date.isoformat() for date in list(newRrule)])
                session.commit()
        session.refresh(podcast)
        for episode, feedEpisode in zip(reversed(podcast.episodes), episodesFromFeed):
            if episode.xml == feedEpisode:
                continue
            else:
                episode.xml = feedEpisode
                session.commit()
    session.close()


ENVIRONEMENT_URL = "localhost:8000" if os.getenv(
    "DEBUG") else "podshift.ddns.net:8080"
LOGGING_CONFIG["formatters"]["access"]["fmt"] = "%(asctime)s " + \
    LOGGING_CONFIG["formatters"]["access"]["fmt"]

scheduler = BackgroundScheduler()
trigger = IntervalTrigger(hours=2, start_date=datetime.now())
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
        session.rollback()
        if "UNIQUE" in e.args[0]:
            podcast = db.getPodcastXML(podcastXML, session)
        else:
            raise HTTPException(status_code=409, detail=f"{e.detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    listDate = dateListRRule(
        freq=form.recurrence,
        dtstart=datetime.date(datetime.now()),
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
