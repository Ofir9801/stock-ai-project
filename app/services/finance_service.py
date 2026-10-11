import logging
import yfinance as yf
from yfinance.exceptions import YFRateLimitError

class DataProviderUnavailable(Exception):
    """The market-data provider is rate limiting us or unreachable."""
    pass

logger = logging.getLogger(__name__)

SECTOR_ETF_MAP = {
    "Technology": "XLK",
    "Financials": "XLF",
    "Healthcare": "XLV",
    "Consumer Discretionary": "XLY",
    "Communication Services": "XLC",
    "Industrials": "XLI",
    "Consumer Defensive": "XLP",
    "Energy": "XLE",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
    "Materials": "XLB",
}


class DataProviderUnavailable(Exception):
    """The market-data provider is rate limiting us or unreachable."""


def _format_summary(summary: str | None) -> str:
    if not summary:
        return "No business summary available."
    if len(summary) > 400:
        return summary[:400] + "..."
    return summary


def _pct_return(prices: list) -> float:
    if not prices or prices[0] == 0:
        return 0.0
    return ((prices[-1] / prices[0]) - 1) * 100


def get_stock_info(ticker: str):
    stock = yf.Ticker(ticker)
    degraded = False  # True when optional data (info / etf / news) is missing

    try:
        info = stock.info or {}
    except Exception as e:
        logger.warning("info failed for %s: %s", ticker, e)
        info = {}
    if not info:
        degraded = True

    try:
        fast_price = stock.fast_info.last_price
    except Exception:
        fast_price = None

    sector = info.get("sector", "Unknown")
    industry = info.get("industry", "Unknown")

    # history is the one mandatory call: without it there is nothing to analyze
    try:
        hist = stock.history(period="1mo")
    except YFRateLimitError as e:
        raise DataProviderUnavailable(str(e)) from e
    if hist.empty:
        raise ValueError(f"No history found for ticker {ticker}")

    stock_prices = hist["Close"].tolist()
    stock_return = _pct_return(stock_prices)

    etf_ticker = SECTOR_ETF_MAP.get(sector, "SPY")
    try:
        etf_prices = yf.Ticker(etf_ticker).history(period="1mo")["Close"].tolist()
        etf_return = round(_pct_return(etf_prices), 2)
    except Exception as e:
        logger.warning("etf history failed for %s: %s", etf_ticker, e)
        etf_return = None  # unknown, not zero
        degraded = True

    formatted_news = []
    try:
        raw_news = stock.news
    except BaseException as e: # noqa: BLE001
        logger.warning("news failed for %s: %s", ticker, e)
        raw_news = None
        degraded = True

    if raw_news:
        for item in raw_news[:3]:
            title = item.get("title") or item.get("headline") or "Market News"
            link = item.get("link") or item.get("url") or "#"
            if link.startswith("/"):
                link = f"https://finance.yahoo.com{link}"
            formatted_news.append({
                "title": title,
                "publisher": item.get("publisher", "Yahoo Finance"),
                "link": link,
            })

    return {
        "name": info.get("longName", ticker),
        "symbol": ticker,
        "price": info.get("currentPrice") or fast_price or 0,
        "sector": sector,
        "industry": industry,
        "stock_return_1mo": round(stock_return, 2),
        "etf_name": etf_ticker,
        "etf_return_1mo": etf_return,
        "history": stock_prices,
        "summary": _format_summary(info.get("longBusinessSummary")),
        "news": formatted_news,
        "degraded": degraded,
    }