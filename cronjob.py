from requests import get
from json import loads, dumps
from dateutil.parser import parse
from utils.xml_reader import (
    extractContents,
    extractLatestEpisode,
    extractTitleFromEpisode,
)
from utils.util import dateListRRule
from db import Database, get_session


def updateFeeds():
    db = Database()
    session = next(get_session())

    podcasts = db.getAllPodcasts(session=session)

    for podcast in podcasts:
        print(podcast.url)

        podcastContent = get(podcast.url).content.decode()

        _, episodesFromFeed = extractContents(podcastContent)
        latestEpisode = extractLatestEpisode(podcastContent)
        latestDbEpisode = podcast.episodes[-1]

        if latestEpisode == latestDbEpisode.xml:
            pass
        elif extractTitleFromEpisode(latestEpisode) == extractTitleFromEpisode(
            latestDbEpisode.xml
        ):
            pass
        else:
            db.addLatestEpisode(latestEpisode, podcast, session)
            for subscription in podcast.customPodcasts:
                dateToPostAt = loads(subscription.dateToPostAt)
                startFreq = dateToPostAt[0]

                rruleStr = dateListRRule(
                    freq=subscription.freq,
                    date=parse(startFreq),
                    interval=subscription.interval,
                    nbEpisodes=len(podcast.episodes),
                    amount=subscription.amount,
                )
                dateToPostAt = dumps(rruleStr)
                db.updateSubscription(subscription, dateToPostAt, session)

        db.refreshEntity(podcast, session)
        for episode, feedEpisode in zip(reversed(podcast.episodes), episodesFromFeed):
            if episode.xml == feedEpisode:
                continue
            else:
                db.updateEpisodeContent(episode, feedEpisode, session)
