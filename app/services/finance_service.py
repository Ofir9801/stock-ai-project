import yfinance as yf # yfinance contains the functions to get stock data from Yahoo Finance

def get_stock_info(ticker: str): # Ticker is a known symbol for a stock
  
    stock = yf.Ticker(ticker)
    info = stock.info
    # gathering last month's data
    hist = stock.history(period="1mo")
    # converting prices to a simple list for the graph
    prices = hist['Close'].tolist()
    
    return { # returning a dictionary with the relevant stock information and price history
        "name": info.get("longName"),
        "price": info.get("currentPrice"),
        "currency": info.get("currency"),
        "summary": info.get("longBusinessSummary")[:300] + "...",
        "history": prices #
    }