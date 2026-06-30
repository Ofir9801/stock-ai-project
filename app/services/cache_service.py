import os
import logging
from datetime import timedelta

from app.db import get_session, StockCache, utcnow

logger = logging.getLogger(__name__)

# How long a cached analysis stays fresh (override via env, in seconds).
CACHE_TTL = timedelta(seconds=int(os.getenv("CACHE_TTL_SECONDS", "3600")))


def get_cached_analysis(ticker: str):
    """Return a fresh cached payload for the ticker, or None on miss / DB down."""
    session = get_session()
    if session is None:
        return None
    try:
        row = session.get(StockCache, ticker)
        if row and (utcnow() - row.updated_at) < CACHE_TTL:
            return {
                "finance_data": row.data,
                "ai_analysis": row.ai_analysis,
                "cached": True,
            }
        return None
    except Exception as e:
        logger.warning(f"Cache read failed for {ticker}: {e}")
        return None
    finally:
        session.close()


def save_analysis(ticker: str, finance_data: dict, ai_analysis: str) -> None:
    """Upsert the latest analysis for the ticker. Best-effort; never raises."""
    session = get_session()
    if session is None:
        return
    try:
        row = session.get(StockCache, ticker)
        if row is None:
            row = StockCache(ticker=ticker)
            session.add(row)
        row.data = finance_data
        row.ai_analysis = ai_analysis
        row.updated_at = utcnow()
        session.commit()
    except Exception as e:
        session.rollback()
        logger.warning(f"Cache write failed for {ticker}: {e}")
    finally:
        session.close()
