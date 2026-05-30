import os
from dotenv import load_dotenv

load_dotenv()

def get_ai_analysis(stock_name: str, summary: str):
    api_key = os.getenv("OPENAI_API_KEY")

    # checking if the API key is set, if not we return a mock analysis for testing purposes
    if not api_key or api_key == "your_api_key_here" or api_key == "":
        return (f"🤖 [MOCK ANALYSIS] Analysis for {stock_name}: "
                f"The stock shows steady movement. Given the business summary, "
                f"investors should watch for upcoming quarterly reports. "
                f"Sentiment Score: 7/10.")

    # if the API key is set, we proceed to call the OpenAI API for a real analysis
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional financial analyst."},
                {"role": "user", "content": f"Analyze this stock: {stock_name}. Summary: {summary}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI Service is active but failed: {e}"