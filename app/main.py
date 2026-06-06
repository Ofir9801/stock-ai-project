from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.finance_service import get_stock_info
from app.services.ai_service import get_ai_analysis

app = FastAPI(title="Stock AI Project API")

# CORS middleware to allow requests from our Streamlit frontend (which runs on a different port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow requests from any origin (useful for development)
    allow_credentials=True,
    allow_methods=["*"],  # allow all types of requests (GET, POST, etc.)
    allow_headers=["*"],  # allow all types of headers
)

@app.get("/stock/{ticker}")
def read_stock(ticker: str):
    try:
        # 1. syncing actual stock data from Yahoo Finance
        finance_data = get_stock_info(ticker)
        
        # 2. sending the data to AI
        ai_insight = get_ai_analysis(finance_data['name'], finance_data['summary'])
        
        return {
            "finance_data": finance_data,
            "ai_analysis": ai_insight
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Stock {ticker} not found")
