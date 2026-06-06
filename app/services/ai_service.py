import os
from dotenv import load_dotenv

load_dotenv()

def get_ai_analysis(stock_data: dict, news_titles: list):
    api_key = os.getenv("OPENAI_API_KEY")

    # checking if the API key is set, if not we return a mock analysis for testing purposes
    if not api_key or api_key == "your_api_key_here" or api_key == "":
        return (f"🤖 [MOCK ANALYSIS] Analysis for {stock_data.get('name', 'Unknown')}: "
                f"The stock shows steady movement. Given the business summary, "
                f"investors should watch for upcoming quarterly reports. "
                f"Sentiment Score: 7/10.")

    # if the API key is set, we proceed to call the OpenAI API for a real analysis
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        # creating a prompt that includes the stock data and recent news headlines for the AI to analyze
        news_context = "\n".join([f"- {t}" for t in news_titles]) if news_titles else "No major headlines."

        prompt = f"""
        Analyze {stock_data['name']} ({stock_data['symbol']}).

        Sector: {stock_data['sector']}
        Industry: {stock_data['industry']}

        Stock 1-month Return: {stock_data['stock_return_1mo']}%
        Sector ETF ({stock_data['etf_name']}) Return: {stock_data['etf_return_1mo']}%

        Business Summary:
        {stock_data['summary']}

        Recent News Headlines:
        {news_context}

        Provide:
        1. Sentiment Score (1-10)
        2. Bull & Bear cases (2 points each)
        3. Competitive Outlook: How does it perform vs. its sector?
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional financial analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ AI Service is active but failed: {e}"
