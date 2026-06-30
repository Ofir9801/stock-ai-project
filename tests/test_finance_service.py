import pandas as pd
from unittest.mock import MagicMock, patch

from app.services import finance_service as fs


def _make_ticker(info, close_prices, news=None):
    """
    Build a fake yfinance Ticker.

    NOTE: we use a real pandas DataFrame for `.history()` so that `hist['Close']`
    works without having to mock `__getitem__`. Mocking item access on a MagicMock
    via a `self`-bound lambda is the documented pitfall — a real DataFrame avoids it.
    """
    ticker = MagicMock()
    ticker.info = info
    ticker.fast_info.last_price = close_prices[-1] if close_prices else None
    ticker.history.return_value = pd.DataFrame({"Close": close_prices})
    ticker.news = news or []
    return ticker


def test_reads_descriptive_fields_from_info_and_maps_etf():
    stock = _make_ticker(
        {
            "sector": "Technology",
            "industry": "Semiconductors",
            "longName": "NVIDIA Corp",
            "currentPrice": 100,
            "longBusinessSummary": "Designs GPUs.",
        },
        [100, 110],
    )
    etf = _make_ticker({}, [50, 55])

    # side_effect feeds the stock on the first yf.Ticker() call, the ETF on the second
    with patch("app.services.finance_service.yf.Ticker", side_effect=[stock, etf]):
        result = fs.get_stock_info("NVDA")

    assert result["name"] == "NVIDIA Corp"          # from stock.info, not fast_info
    assert result["sector"] == "Technology"
    assert result["etf_name"] == "XLK"              # Technology -> XLK
    assert result["stock_return_1mo"] == 10.0
    assert result["etf_return_1mo"] == 10.0
    assert result["summary"] == "Designs GPUs."     # short summary kept as-is


def test_etf_return_guarded_against_empty_history():
    stock = _make_ticker(
        {"sector": "Energy", "longName": "Exxon", "currentPrice": 50},
        [100, 110],
    )
    etf = _make_ticker({}, [])  # empty ETF history -> would IndexError without the guard

    with patch("app.services.finance_service.yf.Ticker", side_effect=[stock, etf]):
        result = fs.get_stock_info("XOM")

    assert result["etf_return_1mo"] == 0.0


def test_news_formatting_and_link_fixup():
    stock = _make_ticker(
        {"sector": "Technology", "longName": "X Corp", "currentPrice": 10},
        [100, 110],
        news=[
            {"title": "Relative link", "link": "/news/1", "publisher": "Yahoo"},
            {"headline": "Headline fallback", "url": "https://example.com/2"},
        ],
    )
    etf = _make_ticker({}, [50, 55])

    with patch("app.services.finance_service.yf.Ticker", side_effect=[stock, etf]):
        result = fs.get_stock_info("X")

    news = result["news"]
    # internal "/..." links are rewritten to absolute Yahoo URLs
    assert news[0]["link"] == "https://finance.yahoo.com/news/1"
    # title falls back to "headline", link falls back to "url"
    assert news[1]["title"] == "Headline fallback"
    assert news[1]["link"] == "https://example.com/2"


def test_price_falls_back_to_fast_info_when_info_lacks_currentprice():
    # .info has no currentPrice -> price should come from fast_info.last_price (110)
    stock = _make_ticker({"sector": "Energy", "longName": "Exxon"}, [100, 110])
    etf = _make_ticker({}, [50, 55])

    with patch("app.services.finance_service.yf.Ticker", side_effect=[stock, etf]):
        result = fs.get_stock_info("XOM")

    assert result["price"] == 110


def test_summary_default_and_truncation():
    assert fs._format_summary(None) == "No business summary available."
    assert fs._format_summary("short") == "short"
    long_summary = "x" * 500
    out = fs._format_summary(long_summary)
    assert out.endswith("...")
    assert len(out) == 403  # 400 chars + "..."
