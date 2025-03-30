import logging

from sqlmodel import Session, create_engine

from app.core.config import settings

logger = logging.getLogger(__name__)


try:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    logger.info("Database engine and session created successfully.")
except Exception as e:
    logger.error(f"Error creating database engine/session: {e}")
    raise


def get_db():
    with Session(engine) as db:
        try:
            yield db
        except Exception as e:
            logger.error(f"Error during database session: {e}")
            raise
