from requests import get
import json
from dateutil.parser import parse
from utils.xml_reader import extractContents, extractLatestEpisode, extractTitleFromEpisode
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
            continue
        elif extractTitleFromEpisode(latestEpisode) == extractTitleFromEpisode(latestDbEpisode.xml):
            continue
        else:
            db.addLatestEpisode(latestEpisode, podcast, session)
            for subscription in podcast.customPodcasts:
                dateToPostAt = json.loads(subscription.dateToPostAt)
                startFreq = dateToPostAt[0]

                rruleStr = dateListRRule(
                    freq=subscription.freq,
                    date=parse(startFreq),
                    interval=subscription.interval,
                    nbEpisodes=len(podcast.episodes),
                    amount=subscription.amount
                )
                dateToPostAt = json.dumps(rruleStr)
                db.updateSubscription(subscription, dateToPostAt, session)

        db.refreshEntity(podcast)

        for episode, feedEpisode in zip(reversed(podcast.episodes), episodesFromFeed):
            if episode.xml == feedEpisode:
                continue
            else:
                db.updateEpisodeContent(episode, feedEpisode, session)

    db.closeSession(session)
