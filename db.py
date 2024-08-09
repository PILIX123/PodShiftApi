from sqlmodel import create_engine, Session
from models.custompodcast import CustomPodcast


DATABASE_URL = "sqlite:///data/db.sqlite"

engine = create_engine(DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session


def getCustomPodcast(customPodcastGUID: str, session: Session) -> CustomPodcast | None:
    return session.get(CustomPodcast, customPodcastGUID)
