import pytest
from sqlmodel import create_engine, Session, SQLModel, select, update

from models.custompodcast import CustomPodcast
from models.podcast import Podcast
from models.episode import Episode

from db import Database

TEST_PODCAST_XML = "TEST_PODCAST_XML"
TEST_PODCAST_XML2 = "TEST_PODCAST_XML2"
TEST_PODCAST_URL = "TEST_PODCAST_URL"
TEST_PODCAST_URL2 = "TEST_PODCAST_URL2"
TEST_EPISODE_XML = "TEST_EPISODE_XML"
TEST_EPISODE_XML2 = "TEST_EPISODE_XML2"
TEST_EPISODE_XML3 = "TEST_EPISODE_XML3"
TEST_CUSTOMPODCAST_UUID = "TEST_CUSTOMPODCAST_UUID"
TEST_CUSTOMPODCAST_DATE = "TEST_CUSTOMPODCAST_DATE"
TEST_CUSTOMPODCAST_UPDATE_DATE = "TEST_CUSTOMPODCAST_UPDATE_DATE"
TEST_CUSTOMPODCAST_FREQ = 1
TEST_CUSTOMPODCAST_INTERVAL = 2
TEST_CUSTOMPODCAST_AMOUNT = 3
TEST_LATEST_PODCAST_XML = "TEST_LATEST_PODCAST_XML"


@pytest.fixture(scope="function")
def session():
    DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(DATABASE_URL, connect_args={
        "check_same_thread": False})
    SQLModel.metadata.create_all(bind=engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(scope="function")
def createDB(session):
    podcast = Podcast(
        xml=TEST_PODCAST_XML,
        url=TEST_PODCAST_URL,
    )
    podcast2 = Podcast(
        xml=TEST_PODCAST_XML2,
        url=TEST_PODCAST_URL2,
    )
    session.add(podcast)
    session.add(podcast2)
    session.commit()
    episode = Episode(
        xml=TEST_EPISODE_XML,
        podcast=podcast,
    )
    session.add(episode)
    session.commit()
    customPodcast = CustomPodcast(
        UUID=TEST_CUSTOMPODCAST_UUID,
        podcast=podcast,
        dateToPostAt=TEST_CUSTOMPODCAST_DATE,
        freq=TEST_CUSTOMPODCAST_FREQ,
        interval=TEST_CUSTOMPODCAST_INTERVAL,
        amount=TEST_CUSTOMPODCAST_AMOUNT
    )
    session.add(customPodcast)
    session.commit()

    return podcast, podcast2, episode, customPodcast


def test_getCustomPodcast(session, createDB):
    db = Database()
    actual = db.getCustomPodcast(TEST_CUSTOMPODCAST_UUID, session)

    assert actual.amount == 3
    assert actual.freq == 1
    assert actual.interval == 2
    assert actual.dateToPostAt == TEST_CUSTOMPODCAST_DATE
    assert actual.UUID == TEST_CUSTOMPODCAST_UUID
    assert actual.podcast.xml == TEST_PODCAST_XML
    assert actual.podcast.url == TEST_PODCAST_URL


def test_getCustomPodcast_no_podcast(session):
    db = Database()
    actual = db.getCustomPodcast(TEST_CUSTOMPODCAST_UUID, session)

    assert actual is None


def test_getPodcastXML(session, createDB):
    db = Database()
    actual = db.getPodcastXML(TEST_PODCAST_XML, session)

    assert actual.xml == TEST_PODCAST_XML
    assert actual.url == TEST_PODCAST_URL


def test_getPodcastXML_no_podcast(session):
    db = Database()
    actual = db.getPodcastXML(TEST_PODCAST_XML, session)

    assert actual is None


def test_createNewPodcast(session):
    db = Database()

    db.createNewPodcast(
        podcastXML=TEST_PODCAST_XML,
        podcastUrl=TEST_PODCAST_URL,
        episodeListXML=[TEST_EPISODE_XML,
                        TEST_EPISODE_XML2, TEST_EPISODE_XML3],
        session=session
    )

    sessionPodcast = session.get(Podcast, 1)
    assert sessionPodcast.xml == TEST_PODCAST_XML
    assert sessionPodcast.url == TEST_PODCAST_URL
    assert sessionPodcast.episodes[0].xml == TEST_EPISODE_XML3
    assert sessionPodcast.episodes[1].xml == TEST_EPISODE_XML2
    assert sessionPodcast.episodes[2].xml == TEST_EPISODE_XML
    assert sessionPodcast.id is not None


def test_createNewPodcast_return_entity(session):
    db = Database()

    actual = db.createNewPodcast(
        podcastXML=TEST_PODCAST_XML,
        podcastUrl=TEST_PODCAST_URL,
        episodeListXML=[TEST_EPISODE_XML,
                        TEST_EPISODE_XML2, TEST_EPISODE_XML3],
        session=session
    )

    assert actual.xml == TEST_PODCAST_XML
    assert actual.url == TEST_PODCAST_URL
    assert actual.episodes[0].xml == TEST_EPISODE_XML3
    assert actual.episodes[1].xml == TEST_EPISODE_XML2
    assert actual.episodes[2].xml == TEST_EPISODE_XML
    assert actual.id is not None


def test_createCustomPodcast(session):
    podcast = Podcast(xml=TEST_PODCAST_XML, url=TEST_PODCAST_URL)
    session.add(podcast)
    session.commit()

    db = Database()

    db.createCustomPodcast(
        jsonDumpDate=TEST_CUSTOMPODCAST_DATE,
        interval=TEST_CUSTOMPODCAST_INTERVAL,
        freq=TEST_CUSTOMPODCAST_FREQ,
        amount=TEST_CUSTOMPODCAST_AMOUNT,
        podcast=podcast,
        session=session
    )

    actual = session.exec(select(CustomPodcast)).one()

    assert actual.UUID is not None
    assert actual.amount == TEST_CUSTOMPODCAST_AMOUNT
    assert actual.interval == TEST_CUSTOMPODCAST_INTERVAL
    assert actual.freq == TEST_CUSTOMPODCAST_FREQ
    assert actual.dateToPostAt == TEST_CUSTOMPODCAST_DATE
    assert actual.podcast.xml == TEST_PODCAST_XML
    assert actual.podcast.url == TEST_PODCAST_URL


def test_createCustomPodcast_return_entity(session):
    podcast = Podcast(xml=TEST_PODCAST_XML, url=TEST_PODCAST_URL)
    session.add(podcast)
    session.commit()

    db = Database()

    actual = db.createCustomPodcast(
        jsonDumpDate=TEST_CUSTOMPODCAST_DATE,
        interval=TEST_CUSTOMPODCAST_INTERVAL,
        freq=TEST_CUSTOMPODCAST_FREQ,
        amount=TEST_CUSTOMPODCAST_AMOUNT,
        podcast=podcast,
        session=session
    )

    assert actual.UUID is not None
    assert actual.amount == TEST_CUSTOMPODCAST_AMOUNT
    assert actual.interval == TEST_CUSTOMPODCAST_INTERVAL
    assert actual.freq == TEST_CUSTOMPODCAST_FREQ
    assert actual.dateToPostAt == TEST_CUSTOMPODCAST_DATE
    assert actual.podcast.xml == TEST_PODCAST_XML
    assert actual.podcast.url == TEST_PODCAST_URL


def test_getAllPodcasts(session, createDB):
    db = Database()

    podcasts = db.getAllPodcasts(session)

    assert type(podcasts) is list
    assert len(podcasts) == 2
    assert podcasts[0].id is not None
    assert podcasts[0].xml == TEST_PODCAST_XML
    assert podcasts[0].url == TEST_PODCAST_URL
    assert len(podcasts[0].episodes) == 1
    assert podcasts[1].id is not None
    assert podcasts[1].xml == TEST_PODCAST_XML2
    assert podcasts[1].url == TEST_PODCAST_URL2
    assert len(podcasts[1].episodes) == 0


def test_addLatestEpisode(session, createDB):
    podcast, _, _, _ = createDB

    db = Database()

    db.addLatestEpisode(
        latestEpisodeContent=TEST_LATEST_PODCAST_XML,
        podcast=podcast,
        session=session
    )

    episodes = session.exec(select(Episode)).all()
    assert podcast.episodes[-1].xml == TEST_LATEST_PODCAST_XML
    assert len(episodes) == 2


def test_updateSubscription(session, createDB):
    _, _, _, customPodcast = createDB

    db = Database()

    db.updateSubscription(
        customPodcast,
        TEST_CUSTOMPODCAST_DATE,
        session
    )

    actual = session.exec(select(CustomPodcast)).one()

    assert actual.dateToPostAt == TEST_CUSTOMPODCAST_DATE


def test_refreshEntity():
    DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(DATABASE_URL, connect_args={
        "check_same_thread": False})
    SQLModel.metadata.create_all(bind=engine)

    with Session(engine) as session:
        podcast = Podcast(
            xml=TEST_PODCAST_XML,
            url=TEST_PODCAST_URL
        )
        session.add(podcast)
        session.commit()

        podcast_id = podcast.id

        with Session(engine) as session2:
            p = session2.exec(select(Podcast).where(
                Podcast.id == podcast_id)).one()

            p.xml = TEST_PODCAST_XML2
            session2.add(p)
            session2.commit()

        db = Database()
        db.refreshEntity(podcast, session)

        assert podcast.xml == TEST_PODCAST_XML2


def test_updateEpisodeContent(session, createDB):
    _, _, episode, _ = createDB
    db = Database()

    db.updateEpisodeContent(episode, TEST_EPISODE_XML2, session)

    actual = session.get(Episode, episode.id)

    assert actual.xml == TEST_EPISODE_XML2


def test_rollback(session, createDB):
    podcast, _, _, _ = createDB

    db = Database()

    podcast.xml = TEST_PODCAST_XML2
    session.add(podcast)

    db.rollback(session)

    assert podcast.xml == TEST_PODCAST_XML
