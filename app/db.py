import os
import logging
from datetime import datetime

from sqlalchemy import create_engine, Column, String, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

# Default points at the docker-compose / local Postgres service. Override via env.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/stockai",
)

Base = declarative_base()


class StockCache(Base):
    """One cached analysis per ticker (upserted on every successful fetch)."""

    __tablename__ = "stock_cache"

    ticker = Column(String, primary_key=True)
    data = Column(JSON, nullable=False)          # the finance_data payload
    ai_analysis = Column(Text, nullable=False)   # the AI text
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# Lazily initialised so the app still boots when no DB is reachable.
_engine = None
_Session = None
_init_failed = False


def init_db() -> bool:
    """
    Create the engine + table on first use. Returns True when the DB is usable.

    Designed to degrade gracefully: if Postgres is unreachable we log a warning
    once and disable caching rather than crashing the request.
    """
    global _engine, _Session, _init_failed

    if _Session is not None:
        return True
    if _init_failed:
        return False

    try:
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        Base.metadata.create_all(_engine)
        _Session = sessionmaker(bind=_engine, expire_on_commit=False)
        logger.info("Database initialised; stock caching enabled.")
        return True
    except Exception as e:
        _init_failed = True
        logger.warning(f"Database unavailable, caching disabled: {e}")
        return False


def get_session():
    """Return a new Session, or None when the DB is not available."""
    if not init_db():
        return None
    return _Session()
