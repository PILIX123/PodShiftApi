from fastapi import FastAPI, Depends
from pyPodcastParser.Podcast import Podcast as pc
from pyPodcastParser.Item import Item
from requests import get
from dateutil.rrule import rrule
from dateutil.parser import parse
from db import init_db, get_session
from sqlmodel import Session, select
from contextlib import asynccontextmanager
from models.forminputmodel import FormInputModel
from models.episode import Episode
from models.podcast import Podcast
from models.custompodcast import CustomPodcast
from datetime import datetime
import json
from xml.etree import ElementTree as ET


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(debug=__debug__, lifespan=lifespan)


@app.get('/')
async def root():
    return {"message": "Hello World"}


@app.post('/PodShift')
async def addFeed(form: FormInputModel):

    return {"message": f"tttte"}


@app.post("/test")
async def addTestPodcast(form: FormInputModel, session: Session = Depends(get_session)):
    t = get(form.url).content
    p = pc(t)

    stmnt = select(Podcast).where(Podcast.title == p.title)
    r = session.exec(stmnt).one_or_none()
    podcast = r if r is not None else Podcast(
        copyright=p.copyright,
        creative_commons=p.creative_commons,
        description=p.description,
        generator=p.generator,
        image_title=p.image_title,
        image_url=p.image_url,
        image_link=p.image_link,
        image_width=p.image_width,
        image_height=p.image_height,
        itunes_author_name=p.itunes_author_name,
        itunes_block=p.itunes_block,
        itunes_complete=p.itunes_complete,
        itunes_explicit=p.itunes_explicit,
        itune_image=p.itune_image,
        itunes_new_feed_url=p.itunes_new_feed_url,
        language=p.language,
        last_build_date=p.last_build_date,
        link=p.link,
        managing_editor=p.managing_editor,
        published_date=p.published_date,
        pubsubhubbub=p.pubsubhubbub,
        owner_name=p.owner_name,
        owner_email=p.owner_email,
        subtitle=p.subtitle,
        title=p.title,
        web_master=p.web_master,
        date_time=p.date_time,
    )
    if (r is None):
        session.add(podcast)
        items: list[Item] = p.items
        if items:
            for episodes in items:
                episode = Episode(
                    author=episodes.author,
                    comments=episodes.comments,
                    creative_commons=episodes.creative_commons,
                    description=episodes.description,
                    enclosure_url=episodes.enclosure_url,
                    enclosure_type=episodes.enclosure_type,
                    enclosure_length=episodes.enclosure_length,
                    itunes_author_name=episodes.itunes_author_name,
                    itunes_block=episodes.itunes_block,
                    itunes_closed_captioned=episodes.itunes_closed_captioned,
                    itunes_duration=episodes.itunes_duration,
                    itunes_explicit=episodes.itunes_explicit,
                    itune_image=episodes.itune_image,
                    itunes_order=episodes.itunes_order,
                    itunes_subtitle=episodes.itunes_subtitle,
                    itunes_summary=episodes.itunes_summary,
                    link=episodes.link,
                    published_date=episodes.published_date,
                    title=episodes.title,
                    date_time=episodes.date_time,
                    podcast_id=podcast.id,
                    podcast=podcast
                )
                session.add(episode)
        session.commit()
        session.refresh(podcast)
    rr = rrule(
        freq=form.recurrence,
        dtstart=datetime.now(),
        interval=form.everyX,
        count=len(p.items)
    )
    customPodcast = CustomPodcast(
        dateToPostAt=json.dumps([date.isoformat() for date in list(rr)]),
        podcast=podcast
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
