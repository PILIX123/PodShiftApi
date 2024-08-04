from datetime import datetime
import json
from xml.etree import ElementTree as ET

from fastapi import FastAPI, Depends, HTTPException
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
        feed = ET.fromstring(get(podcast.url).content.decode())
        channel = feed.find("channel")
        latestEpisode = ET.tostring(
            channel.find("item"), encoding='unicode')
        latestDbEpisode = podcast.episodes[0]
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
                    count=len(podcast.episodes)
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

app = FastAPI(debug=__debug__, lifespan=lifespan)


@app.get('/')
async def root():
    return {"message": "Hello World"}


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
        dtstart=datetime.now(),
        interval=form.everyX,
        count=len(episodes)
    )
    customPodcast = CustomPodcast(
        dateToPostAt=json.dumps([date.isoformat() for date in list(rr)]),
        interval=form.everyX,
        freq=form.recurrence,
        podcast=tp
    )
    session.add(customPodcast)
    session.commit()
    session.refresh(customPodcast)
    return {"url": f"http://localhost:8000/PodShift/{customPodcast.UUID}"}


@app.post("/test")
async def addTestPodcast(form: FormInputModel, session: Session = Depends(get_session)):
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
        dtstart=datetime.now(),
        interval=form.everyX,
        count=len(episodes)
    )
    customPodcast = CustomPodcast(
        dateToPostAt=json.dumps([date.isoformat() for date in list(rr)]),
        interval=form.everyX,
        freq=form.recurrence,
        podcast=tp
    )
    session.add(customPodcast)
    session.commit()
    session.refresh(customPodcast)
    return {"url": f"http://localhost:8000/PodShift/{customPodcast.UUID}"}


@app.get("/PodShift/{customPodcastGUID}")
async def getCustomFeed(customPodcastGUID, session: Session = Depends(get_session)):
    customFeed = session.get(CustomPodcast, customPodcastGUID)
    podcast = customFeed.podcast

    namespaces = {
        "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"
    }
    rss = ET.Element("rss", version='2.0', nsmap=namespaces)
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = podcast.title,
    ET.SubElement(channel, "copyright").text = podcast.copyright
    ET.SubElement(channel, "creative_commons").text = podcast.creative_commons
    ET.SubElement(channel, "description").text = podcast.description
    ET.SubElement(channel, "generator").text = podcast.generator
    ET.SubElement(channel, "language").text = podcast.language
    ET.SubElement(channel, "pubDate").text = podcast.published_date

    # Itunes
    ET.SubElement(channel,
                  f"{namespaces.get("itunes")}author")\
        .text = podcast.itunes_author_name
    ET.SubElement(channel, f"{namespaces.get("itunes")}block")\
        .text = podcast.itunes_block
    ET.SubElement(channel, f"{namespaces.get("itunes")}complete")\
        .text = podcast.itunes_complete
    ET.SubElement(channel, f"{namespaces.get("itunes")}explicit")\
        .text = podcast.itunes_explicit
    ET.SubElement(channel, f"{namespaces.get("itunes")}image", href=podcast.itune_image)\
        .text = podcast.itunes_complete
    if podcast.itunes_new_feed_url:
        ET.SubElement(channel, f"{namespaces.get("itunes")}new-feed-url")\
            .text = podcast.itunes_new_feed_url

    # Image
    image = ET.SubElement(channel, "image")
    ET.SubElement(image, "url").text = podcast.image_url
    ET.SubElement(image, "link").text = podcast.image_link
    ET.SubElement(image, "width").text = podcast.image_width
    ET.SubElement(image, "height").text = podcast.image_height
    ET.SubElement(image, "title").text = podcast.image_title

    for date in json.loads(customFeed.dateToPostAt):
        dt = parse(date)
        if (dt > datetime.now()):
            return
        episodes = customFeed.podcast.episodes
    return
