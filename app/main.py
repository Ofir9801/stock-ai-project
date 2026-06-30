import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.db import init_db
from app.services.finance_service import get_stock_info
from app.services.ai_service import get_ai_analysis
from app.services.cache_service import get_cached_analysis, save_analysis

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialise the DB once at startup (single-threaded), so requests don't race
    # to create the engine. Safe to no-op if the DB is unavailable.
    init_db()
    yield


app = FastAPI(title="Stock AI Project API", lifespan=lifespan)

# CORS: the allowed frontend origin is configurable so it works locally and in Docker/cloud.
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:8501")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
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
    ticker = ticker.upper()
    try:
        # 0. serve from the PostgreSQL cache when we have a fresh entry
        cached = get_cached_analysis(ticker)
        if cached is not None:
            return cached

        # 1. syncing actual stock data from Yahoo Finance
        finance_data = get_stock_info(ticker)

        # extracting just the news titles for the AI analysis
        news_titles = [item["title"] for item in finance_data.get("news", [])]

        # 2. sending the data to the AI service to get a comprehensive analysis
        ai_insight = get_ai_analysis(finance_data, news_titles)

        # 3. persist for next time (best-effort; no-op if the DB is down)
        save_analysis(ticker, finance_data, ai_insight)

        return {
            "finance_data": finance_data,
            "ai_analysis": ai_insight,
            "cached": False,
        }
    except ValueError as e:
        # expected "not found" type errors (e.g. invalid ticker / no history)
        logger.error(f"Ticker error for '{ticker}': {e}", exc_info=True)
        raise HTTPException(status_code=404, detail="Ticker not found or has no available data.")
    except Exception as e:
        # log the full error internally, return a generic message to the client
        logger.error(f"Unexpected server error for '{ticker}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred while processing the request.")
