from app.core.config import settings
from sqlmodel import Session, create_engine

engine = create_engine(settings.DATABASE_URL, echo=False)


def get_db():
    with Session(engine) as session:
        yield session
