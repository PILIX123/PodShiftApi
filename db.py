from sqlmodel import create_engine, Session, select

from models.custompodcast import CustomPodcast
from models.podcast import Podcast
from models.episode import Episode

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

    def createCustomPodcast(self, jsonDumpDate: str, interval: int, freq: int, podcast: Podcast, amount: int, session: Session) -> CustomPodcast:
        customPodcast = CustomPodcast(
            dateToPostAt=jsonDumpDate,
            interval=interval,
            freq=freq,
            podcast=podcast,
            amount=amount
        )
        session.add(customPodcast)
        session.commit()
        session.refresh(customPodcast)

        return customPodcast
