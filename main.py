from datetime import datetime
import json
from xml.etree import ElementTree as ET

from fastapi import FastAPI, Depends, HTTPException, Response
from requests import get
from dateutil.rrule import rrule
from dateutil.parser import parse
from sqlalchemy.exc import IntegrityError

from sqlmodel import Session, select
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from db import init_db, get_session
from models.forminputmodel import FormInputModel
from models.episode import Episode
from models.podcast import Podcast
from models.custompodcast import CustomPodcast


def updateFeeds():
    session = next(get_session())
    stmnt = select(Podcast)
    r = session.exec(stmnt)
    for podcast in r:
        print(podcast.url)
        feed = ET.fromstring(get(podcast.url).content.decode())
        channel = feed.find("channel")
        latestEpisode = ET.tostring(
            channel.find("item"), encoding='unicode')
        latestDbEpisode = podcast.episodes[0]
        if latestEpisode == latestDbEpisode.xml:
            print(f"no changes for {podcast.url}")
            continue
        else:
            print(f"updating {podcast.url}")
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


scheduler = BackgroundScheduler()
trigger = IntervalTrigger(hours=2, start_date=datetime.now())
scheduler.add_job(updateFeeds, trigger)
scheduler.start()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    scheduler.shutdown()

app = FastAPI(title="PodShiftAPI", lifespan=lifespan)


@app.post('/PodShift')
async def addFeed(form: FormInputModel, session: Session = Depends(get_session)):
    root = ET.fromstring(get(form.url).content.decode())
    channel = root.find("channel")
    episodes = []
    for item in channel.findall("item"):
        episodes.append(ET.tostring(item, encoding='unicode'))
        channel.remove(item)
    podcast = ET.tostring(root, encoding='unicode')
    tp = Podcast(xml=podcast, url=form.url)
    session.add(tp)
    if episodes:
        for episode in reversed(episodes):
            te = Episode(xml=episode, podcast=tp)
            session.add(te)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        if "UNIQUE" in e.args[0]:
            tp = session.exec(select(Podcast).where(
                Podcast.xml == podcast)).one_or_none()
        else:
            raise HTTPException(status_code=409, detail=f"{e.detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    rr = rrule(
        freq=form.recurrence,
        dtstart=datetime.date(datetime.now()),
        interval=form.everyX,
        count=len(episodes)/form.amountOfEpisode
    )
    customPodcast = CustomPodcast(
        dateToPostAt=json.dumps([date.isoformat() for date in list(rr)]),
        interval=form.everyX,
        freq=form.recurrence,
        podcast=tp,
        amount=form.amountOfEpisode
    )
    session.add(customPodcast)
    session.commit()
    session.refresh(customPodcast)
    return {"url": f"http://podshift.ddns.net:8080/PodShift/{customPodcast.UUID}"}


@app.get("/PodShift/{customPodcastGUID}")
async def getCustomFeed(customPodcastGUID, session: Session = Depends(get_session)):
    customFeed = session.get(CustomPodcast, customPodcastGUID)
    val = customFeed.podcast.xml
    root = ET.fromstring(val)
    channel = root.find("channel")
    channel.find("title").text = f"Custom Frequency of {
        channel.find("title").text}"
    dates = [parse(d) for d in json.loads(customFeed.dateToPostAt)]
    if customFeed.amount < 1:
        for index, date in enumerate(dates):
            if date < datetime.now():
                channel.insert(-(index+1), ET.fromstring(
                    customFeed.podcast.episodes[index].xml))
    else:
        index = 0
        for date in dates:
            if date < datetime.now():
                for i in range(customFeed.amount):
                    channel.insert(-(i+1+index), ET.fromstring(
                        customFeed.podcast.episodes[i+index].xml))
                index += customFeed.amount
    return Response(content=ET.tostring(root, encoding="unicode"), media_type="application/xml")
