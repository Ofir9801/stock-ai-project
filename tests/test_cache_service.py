from datetime import timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.services import cache_service


@pytest.fixture
def sqlite_sessions(monkeypatch):
    """Point cache_service at a shared in-memory SQLite DB.

    StaticPool keeps a single connection so every Session sees the same in-memory
    database (a plain :memory: URL would give each connection a fresh, empty DB).
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    monkeypatch.setattr(cache_service, "get_session", lambda: Session())
    return Session


def test_cache_roundtrip(sqlite_sessions):
    assert cache_service.get_cached_analysis("AAPL") is None  # cold miss

    cache_service.save_analysis("AAPL", {"price": 100}, "analysis text")

    hit = cache_service.get_cached_analysis("AAPL")
    assert hit is not None
    assert hit["cached"] is True
    assert hit["finance_data"] == {"price": 100}
    assert hit["ai_analysis"] == "analysis text"


def test_cache_upsert_overwrites(sqlite_sessions):
    cache_service.save_analysis("AAPL", {"price": 100}, "first")
    cache_service.save_analysis("AAPL", {"price": 200}, "second")

    hit = cache_service.get_cached_analysis("AAPL")
    assert hit["finance_data"] == {"price": 200}
    assert hit["ai_analysis"] == "second"


def test_cache_respects_ttl(sqlite_sessions, monkeypatch):
    # zero TTL -> any stored row is immediately considered stale
    monkeypatch.setattr(cache_service, "CACHE_TTL", timedelta(seconds=0))
    cache_service.save_analysis("AAPL", {"price": 100}, "analysis")
    assert cache_service.get_cached_analysis("AAPL") is None


def test_cache_degrades_gracefully_when_db_unavailable(monkeypatch):
    # simulate a down/unreachable database: get_session returns None
    monkeypatch.setattr(cache_service, "get_session", lambda: None)

    # a read returns a clean miss instead of raising
    assert cache_service.get_cached_analysis("AAPL") is None

    # a write is a no-op instead of crashing the request path
    cache_service.save_analysis("AAPL", {"price": 100}, "analysis")
