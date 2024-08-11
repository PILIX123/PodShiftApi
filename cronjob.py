from requests import get
import json
from dateutil.rrule import rrule
from dateutil.parser import parse
# TODO: Needs more abstraction this shouldnt be here
from xml.etree import ElementTree as ET
from db import get_session
from sqlmodel import select
from models.podcast import Podcast
from models.episode import Episode

# TOD: refactor this


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
