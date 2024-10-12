from sqlmodel import create_engine, Session, select

from models.custompodcast import CustomPodcast
from models.podcast import Podcast
from models.episode import Episode
from custom_exceptions.no_podcast import NoPodcastException

DATABASE_URL = "sqlite:///data/db.sqlite"

engine = create_engine(DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session


class Database():

    def getCustomPodcast(self, customPodcastGUID: str, session: Session) -> CustomPodcast | None:
        return session.get(CustomPodcast, customPodcastGUID)

    def getPodcastXML(self, podcastXML: str, session: Session) -> Podcast:
        return session.exec(select(Podcast).where(Podcast.xml == podcastXML)).one_or_none()

    def createNewPodcast(self, podcastXML: str, podcastUrl: str, episodeListXML: list[str], session: Session) -> Podcast:
        podcast = Podcast(xml=podcastXML, url=podcastUrl)
        session.add(podcast)
        if episodeListXML:
            for episodeXML in reversed(episodeListXML):
                episode = Episode(xml=episodeXML, podcast=podcast)
                session.add(episode)
        session.commit()
        session.refresh(podcast)
        return podcast

    def createCustomPodcast(self, jsonDumpDate: str, interval: int, freq: int, podcast: Podcast, amount: int, uuid: str, session: Session) -> CustomPodcast:
        customPodcast = CustomPodcast(
            dateToPostAt=jsonDumpDate,
            interval=interval,
            freq=freq,
            podcast=podcast,
            amount=amount,
            UUID=uuid
        )
        session.add(customPodcast)
        session.commit()
        session.refresh(customPodcast)

        return customPodcast

    def getAllPodcasts(self, session: Session) -> list[Podcast]:
        r = session.exec(select(Podcast))
        return list(r)

    def updateCustomPodcast(self, podcastUUID: str, freq: int, interval: int, amount: int, dateToPostAt: str, session: Session):
        customPodcast = session.get(CustomPodcast, podcastUUID)
        if (customPodcast is None):
            raise NoPodcastException(message="No podcast found")

    def addLatestEpisode(self, latestEpisodeContent: str, podcast: Podcast, session: Session):
        podcast.episodes.append(
            Episode(xml=latestEpisodeContent, podcast=podcast))
        session.commit()

    def updateSubscription(self, subscription: CustomPodcast, dateToPostAt: str, session: Session):
        subscription.dateToPostAt = dateToPostAt
        session.commit()

    def refreshEntity(self, entity: Podcast | Episode | CustomPodcast, session: Session):
        session.refresh(entity)

    def updateEpisodeContent(self, episode: Episode, episodeContent: str, session: Session):
        episode.xml = episodeContent
        session.commit()

    def rollback(self, session: Session):
        session.rollback()
