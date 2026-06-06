import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# page settings
st.set_page_config(page_title="AI Stock Research", layout="wide")

st.title("📈 AI Stock Research Dashboard")
st.subheader("Professional Sectoral & Competitive Analysis")
st.markdown("---")

# input for stock ticker
ticker = st.text_input("Enter Stock Ticker (e.g. NVDA, AAPL, MSFT):", "NVDA").upper()

if st.button("Generate Comprehensive Report"):
    with st.spinner(f"Fetching sectoral data and generating AI insights for {ticker}..."):
        try:
            # making a request to our FastAPI backend to get both financial data and AI analysis
            response = requests.get(f"{BACKEND_URL}/stock/{ticker}")
            
            if response.status_code == 200:
                data = response.json()
                f_data = data['finance_data']
                ai_data = data['ai_analysis']

                # 2. displaying the data in two columns
                col1, col2 = st.columns([1, 1])

                with col1:
                    st.subheader(f"📊 Financials: {f_data['name']}")
                    st.metric("Current Price", f"${f_data['price']}")
                    
                    # adding graph:
                    st.write("**Price History (Last 30 Days):**")
                    st.line_chart(f_data['history'])
                    
                    st.write("**Business Summary:**")
                    st.write(f_data['summary'])
                with col2:
                    st.subheader("🤖 AI Market Insight")
                    st.success(ai_data) # displays the analysis in a green box
            else:
                st.error("Ticker not found. Please try again.")
        except Exception as e:
            st.error(f"Could not connect to Backend. Is the FastAPI server running?")

st.markdown("---")
st.warning("""
**⚠️ Disclaimer:** This tool is for educational purposes only. The AI-generated analysis and financial data 
provided do not constitute financial advice. The developer is not a licensed financial advisor. 
Always perform your own due diligence before making investment decisions.
""")
st.caption(f"© 2024 Stock AI Project | Data: Yahoo Finance | AI: OpenAI GPT-4o-mini")