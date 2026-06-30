import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# System persona shared by every provider.
SYSTEM_PROMPT = "You are a professional financial analyst."

# Default model per provider (override via env without touching code).
# Cost-conscious defaults; bump to a larger model via env for deeper analysis.
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5")

# Hard timeout (seconds) for an LLM call, so a hung provider can't tie up a worker.
AI_TIMEOUT_SECONDS = float(os.getenv("AI_TIMEOUT_SECONDS", "30"))


def _placeholder(value: str | None) -> bool:
    """True when an API key is missing or left as a template placeholder."""
    return not value or value in ("your_api_key_here", "")


def _build_prompt(stock_data: dict, news_titles: list) -> str:
    news_context = "\n".join(f"- {t}" for t in news_titles) if news_titles else "No major headlines."
    return f"""
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


def _analyze_with_claude(prompt: str) -> str:
    from anthropic import Anthropic

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), timeout=AI_TIMEOUT_SECONDS)
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    # response.content is a list of blocks; keep only the text blocks
    return "".join(block.text for block in message.content if block.type == "text")


def _analyze_with_openai(prompt: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=AI_TIMEOUT_SECONDS)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def _resolve_provider() -> str:
    """
    Decide which provider to use.

    AI_PROVIDER=claude|openai forces a specific provider; the default "auto"
    prefers Claude, falls back to OpenAI, then to a mock when no key is set.
    """
    requested = os.getenv("AI_PROVIDER", "auto").lower()
    has_claude = not _placeholder(os.getenv("ANTHROPIC_API_KEY"))
    has_openai = not _placeholder(os.getenv("OPENAI_API_KEY"))

    if requested == "claude":
        return "claude" if has_claude else "mock"
    if requested == "openai":
        return "openai" if has_openai else "mock"

    # auto
    if has_claude:
        return "claude"
    if has_openai:
        return "openai"
    return "mock"


def _mock_analysis(stock_data: dict) -> str:
    return (
        f"🤖 [MOCK ANALYSIS] Analysis for {stock_data.get('name', 'Unknown')}: "
        f"The stock shows steady movement. Given the business summary, "
        f"investors should watch for upcoming quarterly reports. "
        f"Sentiment Score: 7/10."
    )


def get_ai_analysis(stock_data: dict, news_titles: list) -> str:
    """Route the analysis request to the configured AI provider."""
    provider = _resolve_provider()

    if provider == "mock":
        # no real key configured — return a deterministic mock so the app still works
        return _mock_analysis(stock_data)

    prompt = _build_prompt(stock_data, news_titles)
    try:
        if provider == "claude":
            return _analyze_with_claude(prompt)
        return _analyze_with_openai(prompt)
    except Exception as e:
        # log the full error internally, return a generic message to the client
        logger.error(f"AI analysis failed (provider={provider}): {e}", exc_info=True)
        return "⚠️ AI analysis is temporarily unavailable. Please try again later."
