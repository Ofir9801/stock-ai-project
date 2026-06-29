from app.services import cache_service


def test_cache_degrades_gracefully_when_db_unavailable(monkeypatch):
    # simulate a down/unreachable database: get_session returns None
    monkeypatch.setattr(cache_service, "get_session", lambda: None)

    # a read returns a clean miss instead of raising
    assert cache_service.get_cached_analysis("AAPL") is None

    # a write is a no-op instead of crashing the request path
    cache_service.save_analysis("AAPL", {"price": 100}, "analysis")
