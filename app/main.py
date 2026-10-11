import os
import re
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.services.finance_service import get_stock_info, DataProviderUnavailable
from app.services.ai_service import get_ai_analysis, is_fallback_analysis
from app.services.cache_service import get_cached_analysis, save_analysis

# --- Logging Setup ---
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# --- Constants ---
TICKER_RE = re.compile(r"^[A-Z0-9.\-]{1,10}$")


# --- App Lifecycle ---
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
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Endpoints ---
@app.get("/")
def home():
    return {"status": "The server is alive"}


@app.get("/api/stock/{ticker}")
def read_stock(ticker: str):
    # 1. Validate and sanitize input to prevent unnecessary API calls
    ticker = ticker.strip().upper()
    if not TICKER_RE.match(ticker):
        raise HTTPException(status_code=404, detail="Ticker not found or has no available data.")

    try:
        # 2. Serve from PostgreSQL cache when we have a fresh entry
        cached = get_cached_analysis(ticker)
        if cached is not None:
            return cached

        # 3. Fetch actual stock data from Yahoo Finance with graceful degradation
        try:
            finance_data = get_stock_info(ticker)
        except DataProviderUnavailable:
            # If rate-limited, try to serve stale but valid data
            stale = get_cached_analysis(ticker, allow_stale=True)
            if stale is not None:
                return stale
            raise  # Re-raise to be caught by the outer except block

        # 4. Partial data fallback: prefer an older complete analysis over a fresh poor one
        if finance_data.get("degraded"):
            stale = get_cached_analysis(ticker, allow_stale=True)
            if stale is not None:
                return stale

        # 5. Generate AI analysis
        news_titles = [item["title"] for item in finance_data.get("news", [])]
        ai_insight = get_ai_analysis(finance_data, news_titles)

        # 6. Persist ONLY if data is healthy and AI response is genuine (not mock/error)
        if not finance_data.get("degraded") and not is_fallback_analysis(ai_insight):
            save_analysis(ticker, finance_data, ai_insight)

        return {
            "finance_data": finance_data,
            "ai_analysis": ai_insight,
            "cached": False,
        }

    # 7. Error Handling
    except ValueError as e:
        # Expected "not found" type errors (e.g., invalid ticker / no history)
        logger.error(f"Ticker error for '{ticker}': {e}", exc_info=True)
        raise HTTPException(status_code=404, detail="Ticker not found or has no available data.")
    
    except DataProviderUnavailable as e:
        # Specific handling for rate limiting / API outages
        logger.error(f"Data provider unavailable for '{ticker}': {e}")
        raise HTTPException(
            status_code=503,
            detail="Market data provider is rate limiting us. Please try again in a minute.",
        )
    
    except Exception as e:
        # Catch-all for unexpected server errors
        logger.error(f"Unexpected server error for '{ticker}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred while processing the request.")