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
    with st.spinner(f"Analyzing {ticker}..."):
        try:
            response = requests.get(f"{BACKEND_URL}/stock/{ticker}")
            
            if response.status_code == 200:
                data = response.json()
                f_data = data['finance_data']
                ai_data = data['ai_analysis']

                # displaying key metrics in a 4-column layout
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Price", f"${f_data['price']}")
                m2.metric("Sector", f_data['sector'])
                m3.metric("ETF", f_data['etf_name'])

                # calculating alpha (excess return)
                alpha = round(f_data['stock_return_1mo'] - f_data['etf_return_1mo'], 2)
                m4.metric("vs Sector", f"{alpha}%", delta=alpha)

                st.markdown("---")

                col1, col2 = st.columns([1, 1.2])

                with col1:
                    st.subheader("Price Movement (30D)")
                    st.line_chart(f_data['history'])
                    
                    with st.expander("Business Summary"):
                        st.write(f_data['summary'])
                    
                    st.write("📰 **Latest News**")
                    for n in f_data.get('news', []):
                        st.markdown(f"- [{n['title']}]({n['link']})")

                with col2:
                    st.subheader("🤖 AI Analysis & Competitive Outlook")
                    st.markdown(ai_data)

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
