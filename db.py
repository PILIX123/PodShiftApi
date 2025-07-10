from sqlmodel import create_engine, Session, select
from sqlalchemy.engine import Engine
from alembic import config, script
from alembic.runtime import migration

from migrations import env

from models.custompodcast import CustomPodcast, CustomPodcastUpdate
from models.podcast import Podcast
from models.episode import Episode
from custom_exceptions.no_podcast import NoPodcastException

DATABASE_URL = "sqlite:///data/db.sqlite"

engine = create_engine(DATABASE_URL)
cfg = config.Config("alembic.ini")


def check_current_head(alembic_cfg: config.Config, connectable: Engine):
    directory = script.ScriptDirectory.from_config(alembic_cfg)
    with connectable.begin() as connection:
        context = migration.MigrationContext.configure(connection)
        return set(context.get_current_heads()) == set(directory.get_heads())


need_update = check_current_head(cfg, engine)
if need_update:
    env.run_migrations_online()


def get_session():
    with Session(engine) as session:
        yield session


class Database:

    def getCustomPodcast(
        self, customPodcastGUID: str, session: Session
    ) -> CustomPodcast | None:
        return session.get(CustomPodcast, customPodcastGUID)

    def getPodcastXML(self, podcastXML: str, session: Session) -> Podcast:
        return session.exec(
            select(Podcast).where(Podcast.xml == podcastXML)
        ).one_or_none()

    def createNewPodcast(
        self,
        podcastXML: str,
        podcastUrl: str,
        episodeListXML: list[str],
        title: str,
        session: Session,
    ) -> Podcast:
        podcast = Podcast(xml=podcastXML, url=podcastUrl, title=title)
        session.add(podcast)
        if episodeListXML:
            for episodeXML in reversed(episodeListXML):
                episode = Episode(xml=episodeXML, podcast=podcast)
                session.add(episode)
        session.commit()
        session.refresh(podcast)
        return podcast

    def createCustomPodcast(
        self,
        jsonDumpDate: str,
        interval: int,
        freq: int,
        podcast: Podcast,
        amount: int,
        uuid: str,
        session: Session,
    ) -> CustomPodcast:
        customPodcast = CustomPodcast(
            dateToPostAt=jsonDumpDate,
            interval=interval,
            freq=freq,
            podcast=podcast,
            amount=amount,
            UUID=uuid,
        )
        session.add(customPodcast)
        session.commit()
        session.refresh(customPodcast)

        return customPodcast

    def getAllPodcasts(self, session: Session) -> list[Podcast]:
        r = session.exec(select(Podcast))
        return list(r)

    def updateCustomPodcast(
        self,
        podcastUUID: str,
        updateCustomPodcast: CustomPodcastUpdate,
        session: Session,
    ):
        customPodcast = session.get(CustomPodcast, podcastUUID)
        if customPodcast is None:
            raise NoPodcastException()
        podcastData = updateCustomPodcast.model_dump(exclude_unset=True)
        customPodcast.sqlmodel_update(podcastData)
        session.add(customPodcast)
        session.commit()
        session.refresh(customPodcast)
        return customPodcast

    def deleteCustomPodcast(self, podcastUUID: str, session: Session):
        customPodcast = session.get(CustomPodcast, podcastUUID)
        if customPodcast is None:
            raise NoPodcastException()
        session.delete(customPodcast)
        session.commit()

    def addLatestEpisode(
        self, latestEpisodeContent: str, podcast: Podcast, session: Session
    ):
        podcast.episodes.append(
            Episode(xml=latestEpisodeContent, podcast=podcast))
        session.commit()

    def updateEpisodeContent(
        self, episode: Episode, episodeContent: str, session: Session
    ):
        episode.xml = episodeContent
        session.commit()

    def updateSubscription(
        self, subscription: CustomPodcast, dateToPostAt: str, session: Session
    ):
        subscription.dateToPostAt = dateToPostAt
        session.commit()

    def refreshEntity(
        self, entity: Podcast | Episode | CustomPodcast, session: Session
    ):
        session.refresh(entity)

    def rollback(self, session: Session):
        session.rollback()
