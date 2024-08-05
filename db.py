from sqlmodel import create_engine, SQLModel, Session

DATABASE_URL = "sqlite:///data/db.sqlite"

engine = create_engine(DATABASE_URL)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
