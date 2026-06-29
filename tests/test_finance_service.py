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


def test_summary_default_and_truncation():
    assert fs._format_summary(None) == "No business summary available."
    assert fs._format_summary("short") == "short"
    long_summary = "x" * 500
    out = fs._format_summary(long_summary)
    assert out.endswith("...")
    assert len(out) == 403  # 400 chars + "..."
