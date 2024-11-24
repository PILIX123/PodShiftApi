import os
from datetime import datetime
import json
from uuid import uuid1

from fastapi import FastAPI, Depends, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
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
from models.responsemodel import ResponseModel, PodcastResponseModel
from models.updatemodel import FormUpdateModel
from models.customerror import Detail
from models.custompodcast import CustomPodcastUpdate
from custom_exceptions.no_podcast import NoPodcastException
from utils.xml_reader import createPodcast, extractContents, isValidXML, extractTitleFromRoot
from utils.util import dateListRRule
from cronjob import updateFeeds


DEBUG = os.getenv("DEBUG") == "True"
ENVIRONEMENT_URL = "localhost:8000" if DEBUG else "podshift.net:8080"
LOGGING_CONFIG["formatters"]["access"]["fmt"] = (
    "%(asctime)s " + LOGGING_CONFIG["formatters"]["access"]["fmt"]
)

scheduler = BackgroundScheduler()
trigger = (
    IntervalTrigger(minutes=10, start_date=datetime.now())
    if DEBUG
    else IntervalTrigger(hours=2, start_date=datetime.now())
)
scheduler.add_job(updateFeeds, trigger)
scheduler.start()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    scheduler.shutdown()


docs_url = "/docs" if DEBUG else None
app = FastAPI(title="PodShiftAPI", lifespan=lifespan, docs_url=docs_url)
db = Database()

app.add_middleware(
    CORSMiddleware,
    allow_origins={"*"},
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/PodShift",
    response_model=ResponseModel,
    responses={400: {"model": Detail}, 409: {
        "model": Detail}, 500: {"model": Detail}},
)
async def addFeed(form: FormInputModel, session: Session = Depends(get_session)):
    try:
        url = get(form.url)
    except:
        return JSONResponse(
            status_code=400, content={"detail": "The given URL isnt valid"}
        )
    try:
        podcastContent = url.content.decode()
        isValidXML(podcastContent)
    except:
        return JSONResponse(
            status_code=400,
            content={"detail": "The url content wasnt an XML containing RSS"},
        )

    podcastXML, episodesXMLList = extractContents(podcastContent)

    title = extractTitleFromRoot(podcastXML)
    try:
        podcast = db.createNewPodcast(
            podcastXML=podcastXML,
            podcastUrl=form.url,
            episodeListXML=episodesXMLList,
            title=title,
            session=session,
        )
    except IntegrityError as e:
        db.rollback(session)
        if "UNIQUE" in e.args[0]:
            podcast = db.getPodcastXML(podcastXML, session)
        else:
            return JSONResponse(status_code=409, content={"detail": f"{e.detail}"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

    listDate = dateListRRule(
        freq=form.recurrence,
        date=datetime.date(datetime.now()),
        interval=form.everyX,
        nbEpisodes=len(episodesXMLList),
        amount=form.amountOfEpisode,
    )
    jsonDumps = json.dumps(listDate)
    uuid = str(uuid1())
    customPodcast = db.createCustomPodcast(
        jsonDumpDate=jsonDumps,
        interval=form.everyX,
        freq=form.recurrence,
        podcast=podcast,
        amount=form.amountOfEpisode,
        uuid=uuid,
        session=session,
    )
    # TODO: Got to edit this to return all the info needed for the list to be populated
    return JSONResponse(
        content=jsonable_encoder(
            ResponseModel(
                url=f"http://{ENVIRONEMENT_URL}/PodShift/{customPodcast.UUID}"
            )
        )
    )


@app.get(
    "/PodShift/{customPodcastGUID}",
    response_class=Response,
    responses={200: {"content": {"application/xml": {}}},
               404: {"model": Detail}},
)
async def getCustomFeed(customPodcastGUID, session: Session = Depends(get_session)):
    customFeed = db.getCustomPodcast(customPodcastGUID, session)

    if customFeed is None:
        return JSONResponse(status_code=404, content={"detail": "No podcast found"})

    content = createPodcast(
        podcastContent=customFeed.podcast.xml,
        parsedDates=[parse(d) for d in json.loads(customFeed.dateToPostAt)],
        amount=customFeed.amount,
        listEpisodes=[ep.xml for ep in customFeed.podcast.episodes],
    )

    return Response(content=content, media_type="application/xml")


@app.put(
    "/PodShift/{customPodcastGUID}",
    response_model=PodcastResponseModel,
    responses={
        200: {"content": {}},
        404: {"model": Detail},
        500: {"model": Detail},
    },
)
async def updateCustomFeed(
    customPodcastGUID,
    updateModel: FormUpdateModel,
    session: Session = Depends(get_session),
):
    try:
        customFeed = db.getCustomPodcast(customPodcastGUID, session)

        if customFeed is None:
            raise NoPodcastException

        newDates = dateListRRule(
            freq=updateModel.recurrence,
            date=datetime.date(datetime.now()),
            interval=updateModel.everyX,
            nbEpisodes=len(customFeed.podcast.episodes) -
            updateModel.currentEpisode,
            amount=updateModel.amountOfEpisode,
        )

        podcastToUpdate = CustomPodcastUpdate(
            podcast_id=customFeed.podcast_id,
            dateToPostAt=json.dumps(newDates),
            amount=updateModel.amountOfEpisode,
            freq=updateModel.recurrence,
            interval=updateModel.everyX,
        )

        customPodcast = db.updateCustomPodcast(
            podcastUUID=customPodcastGUID,
            updateCustomPodcast=podcastToUpdate,
            session=session,
        )

        if customPodcast is None:
            raise NoPodcastException

        response = PodcastResponseModel(
            UUID=customPodcast.UUID,
            freq=customPodcast.freq,
            interval=customPodcast.interval,
            url=customFeed.podcast.url,
            title=customFeed.podcast.title,
            amount=customPodcast.amount,
        )
        return JSONResponse(content=jsonable_encoder(response))
    except NoPodcastException:
        return JSONResponse(
            status_code=404, content={"detail": "The requested podcast was not found"}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.delete(
    "/PodShift/{customPodcastGUID}",
    responses={200: {}, 404: {"model": Detail}, 500: {"model": Detail}},
)
async def deleteCustomPodcast(
    customPodcastGUID: str, session: Session = Depends(get_session)
):
    try:
        db.deleteCustomPodcast(customPodcastGUID, session=session)
    except NoPodcastException:
        return JSONResponse(
            status_code=404, content={"detail": "The requested podcast was not found"}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.get(
    "/PodShift/{customPodcastGUID}/content",
    responses={200: {"model": PodcastResponseModel},
               404: {"model": Detail}, 500: {"model": Detail}},
)
async def GetCustomPodcastContent(
    customPodcastGUID: str, session: Session = Depends(get_session)
):
    customPodcast = db.getCustomPodcast(
        customPodcastGUID=customPodcastGUID, session=session)
    if customPodcast is None:
        return JSONResponse(
            status_code=404, content={"detail": "The requested podcast was not found"}
        )
    response = PodcastResponseModel(
        UUID=customPodcast.UUID,
        freq=customPodcast.freq,
        interval=customPodcast.interval,
        amount=customPodcast.amount,
        url=customPodcast.podcast.url,
        title=customPodcast.podcast.title,
    )
    return JSONResponse(content=jsonable_encoder(response))
