from sqlmodel import Session, create_engine

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)

try:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
except Exception as e:
    print(f"Failed to create database engine: {e}")
    raise


def get_db():
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception as e:
            print(f"Error during database session: {e}")
            session.rollback()
            raise
