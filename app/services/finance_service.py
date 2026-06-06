import yfinance as yf

# Mapping of sectors to their corresponding ETFs for broader market analysis
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
    "Materials": "XLB"
}

def get_stock_info(ticker: str):

    stock = yf.Ticker(ticker)
    info = stock.info

    # sector information
    sector = info.get("sector", "Unknown")
    industry = info.get("industry", "Unknown")

    # stock history and news
    hist = stock.history(period="1mo")
    if hist.empty:
        raise ValueError(f"No history found for ticker {ticker}")

    stock_prices = hist['Close'].tolist()
    stock_return = ((stock_prices[-1] / stock_prices[0]) - 1) * 100

    # comparing to sector ETF
    etf_ticker = SECTOR_ETF_MAP.get(sector, "SPY")
    etf = yf.Ticker(etf_ticker)
    etf_hist = etf.history(period="1mo")
    etf_prices = etf_hist['Close'].tolist()
    etf_return = ((etf_prices[-1] / etf_prices[0]) - 1) * 100

    raw_news = stock.news
    formatted_news = []

    if raw_news:
        for item in raw_news[:3]:

            # improved title fallback
            title = item.get("title") or item.get("headline") or "Market News"

            # improved link fallback
            link = item.get("link") or item.get("url") or "#"

            # fix Yahoo internal links
            if link.startswith("/"):
                link = f"https://finance.yahoo.com{link}"

            formatted_news.append({
                "title": title,
                "publisher": item.get("publisher", "Yahoo Finance"),
                "link": link
            })

    return {
        "name": info.get("longName", ticker),
        "symbol": ticker,
        "price": info.get("currentPrice", 0),
        "sector": sector,
        "industry": industry,
        "stock_return_1mo": round(stock_return, 2),
        "etf_name": etf_ticker,
        "etf_return_1mo": round(etf_return, 2),
        "history": stock_prices,
        "summary": info.get("longBusinessSummary", "")[:400] + "...",
        "news": formatted_news
    }
