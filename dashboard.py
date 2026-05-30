import streamlit as st
import requests
import pandas as pd

# page settings
st.set_page_config(page_title="AI Stock Research", layout="wide")

st.title("📈 AI Stock Research Dashboard")
st.markdown("---")

# search bar
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, NVDA):", "AAPL").upper()

if st.button("Run AI Analysis"):
    with st.spinner(f"Analyzing {ticker}..."):
        try:
            # 1. making a request to the FastAPI backend to get stock data and AI analysis
            response = requests.get(f"http://127.0.0.1:8000/stock/{ticker}")
            
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
st.caption("Developed as a CS Student Project")