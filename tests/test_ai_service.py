from types import SimpleNamespace

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


def test_analyze_with_claude_extracts_only_text_blocks(monkeypatch):
    import anthropic

    # response with a (empty) thinking block followed by a text block
    fake_message = SimpleNamespace(content=[
        SimpleNamespace(type="thinking", text=""),
        SimpleNamespace(type="text", text="hello from claude"),
    ])

    class FakeClient:
        def __init__(self, **kwargs):
            self.messages = SimpleNamespace(create=lambda **kw: fake_message)

    monkeypatch.setattr(anthropic, "Anthropic", FakeClient)
    assert ai._analyze_with_claude("prompt") == "hello from claude"


def test_analyze_with_openai_extracts_message_content(monkeypatch):
    import openai

    fake_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="hello from openai"))]
    )

    class FakeClient:
        def __init__(self, **kwargs):
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=lambda **kw: fake_response)
            )

    monkeypatch.setattr(openai, "OpenAI", FakeClient)
    assert ai._analyze_with_openai("prompt") == "hello from openai"
