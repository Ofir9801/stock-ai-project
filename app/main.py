import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.finance_service import get_stock_info
from app.services.ai_service import get_ai_analysis

app = FastAPI(title="Stock AI Project API")
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# CORS middleware to allow requests from our Streamlit frontend (which runs on a different port).
# A wildcard origin ("*") combined with allow_credentials=True is invalid/insecure, so we
# pin a specific origin instead.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],  # allow all types of requests (GET, POST, etc.)
    allow_headers=["*"],  # allow all types of headers
)
# the following is for testing
@app.get("/")
def home():
    return {"status": "The server is alive"}

@app.get("/api/stock/{ticker}")
def read_stock(ticker: str):
    try:
        # 1. syncing actual stock data from Yahoo Finance
        finance_data = get_stock_info(ticker)

        # extracting just the news titles for the AI analysis
        news_titles = [item["title"] for item in finance_data.get("news", [])]

        # 2. sending the data to the AI service to get a comprehensive analysis
        ai_insight = get_ai_analysis(finance_data, news_titles)

        return {
            "finance_data": finance_data,
            "ai_analysis": ai_insight
        }
    except ValueError as e:
        # expected "not found" type errors (e.g. invalid ticker / no history)
        logger.error(f"Ticker error for '{ticker}': {e}", exc_info=True)
        raise HTTPException(status_code=404, detail="Ticker not found or has no available data.")
    except Exception as e:
        # log the full error internally, return a generic message to the client
        logger.error(f"Unexpected server error for '{ticker}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred while processing the request.")
