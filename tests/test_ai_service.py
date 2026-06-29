from app.services import ai_service as ai


def test_auto_prefers_claude_when_both_keys_present(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-test")
    monkeypatch.setenv("AI_PROVIDER", "auto")
    assert ai._resolve_provider() == "claude"


def test_auto_falls_back_to_openai_then_mock(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-test")
    monkeypatch.setenv("AI_PROVIDER", "auto")
    assert ai._resolve_provider() == "openai"

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert ai._resolve_provider() == "mock"


def test_get_ai_analysis_returns_mock_without_keys(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    out = ai.get_ai_analysis({"name": "NVDA"}, [])
    assert "MOCK" in out


def test_get_ai_analysis_routes_to_claude(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("AI_PROVIDER", "claude")

    called = {}

    def fake_claude(prompt):
        called["prompt"] = prompt
        return "claude analysis"

    monkeypatch.setattr(ai, "_analyze_with_claude", fake_claude)

    stock = {
        "name": "NVDA", "symbol": "NVDA", "sector": "Technology",
        "industry": "Semis", "stock_return_1mo": 10, "etf_name": "XLK",
        "etf_return_1mo": 8, "summary": "GPUs",
    }
    out = ai.get_ai_analysis(stock, ["headline one"])
    assert out == "claude analysis"
    assert "NVDA" in called["prompt"]  # prompt was built and passed through
