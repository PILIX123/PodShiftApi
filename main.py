from fastapi import FastAPI, Depends
from models.forminputmodel import FormInputModel
from pyPodcastParser.Podcast import Podcast as pc
from pyPodcastParser.Item import Item
from requests import get
from utils.parser import create_rrule_from_dates
from contextlib import asynccontextmanager
from db import init_db, get_session
from models.episode import Episode
from models.podcast import Podcast
from models.user import User
from sqlmodel import Session


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
    rrule = create_rrule_from_dates(form.recurrence)
    return {"message": f"{rrule.count()}"}


@app.post("/test")
async def addTestPodcast(form: FormInputModel, session: Session = Depends(get_session)):
    t = get(form.url).content
    p = pc(t)
    podcast = Podcast(
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
    session.add(podcast)
    testing: list[Item] = p.items
    if testing:
        for episodes in testing:
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


@app.get("/PodShift/{userID}/{podcastID}")
async def getCustomFeed(userID, podcastID):
    pass
