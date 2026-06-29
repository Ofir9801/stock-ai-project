from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

# raise_server_exceptions=False so we can assert on 500 responses instead of re-raising
client = TestClient(app, raise_server_exceptions=False)

FAKE_FINANCE = {
    "name": "Apple Inc.",
    "symbol": "AAPL",
    "price": 200,
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "stock_return_1mo": 5.0,
    "etf_name": "XLK",
    "etf_return_1mo": 3.0,
    "history": [190, 200],
    "summary": "Makes iPhones.",
    "news": [{"title": "Apple news", "publisher": "Yahoo", "link": "#"}],
}


def test_read_stock_success():
    with patch("app.main.get_cached_analysis", return_value=None), \
         patch("app.main.save_analysis"), \
         patch("app.main.get_stock_info", return_value=FAKE_FINANCE), \
         patch("app.main.get_ai_analysis", return_value="the analysis"):
        resp = client.get("/api/stock/aapl")

    assert resp.status_code == 200
    body = resp.json()
    assert body["finance_data"]["symbol"] == "AAPL"
    assert body["ai_analysis"] == "the analysis"
    assert body["cached"] is False


def test_read_stock_cache_hit_short_circuits():
    cached = {"finance_data": FAKE_FINANCE, "ai_analysis": "cached one", "cached": True}
    with patch("app.main.get_cached_analysis", return_value=cached), \
         patch("app.main.get_stock_info") as mock_fetch:
        resp = client.get("/api/stock/AAPL")

    assert resp.status_code == 200
    assert resp.json()["cached"] is True
    mock_fetch.assert_not_called()  # cache hit must skip the live fetch


def test_value_error_returns_404_with_generic_message():
    with patch("app.main.get_cached_analysis", return_value=None), \
         patch("app.main.get_stock_info", side_effect=ValueError("no history found for FAKE")):
        resp = client.get("/api/stock/FAKE")

    assert resp.status_code == 404
    detail = resp.json()["detail"]
    assert "no history found" not in detail  # raw error must not leak to the client


def test_unexpected_error_returns_500_with_generic_message():
    with patch("app.main.get_cached_analysis", return_value=None), \
         patch("app.main.get_stock_info", side_effect=RuntimeError("boom secret")):
        resp = client.get("/api/stock/AAPL")

    assert resp.status_code == 500
    assert "boom secret" not in resp.json()["detail"]
