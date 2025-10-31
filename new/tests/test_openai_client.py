import pytest
import respx
import httpx

from app.services.openai_client import generate_chat_reply, extract_loan_offers_from_tavily
from app.services.errors import AuthenticationError, RateLimitError, APIError, ConfigError


@respx.mock
def test_openai_generate_success(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": "Hello from test."}}]
            },
        )
    )
    out = generate_chat_reply("Hi")
    assert "Hello from test." in out


@respx.mock
def test_openai_auth_error(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=httpx.Response(401, json={"error": {"message": "bad key"}})
    )
    with pytest.raises(AuthenticationError):
        generate_chat_reply("Hi")


@respx.mock
def test_openai_rate_limit(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=httpx.Response(429, json={"error": {"message": "rate limit"}})
    )
    with pytest.raises(RateLimitError):
        generate_chat_reply("Hi")


def test_openai_missing_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ConfigError):
        generate_chat_reply("Hi")


@respx.mock
def test_extract_loan_offers_success(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": (
                                '{"loan_offers": [ '
                                '{"bank_name": "HDFC", "interest_rate": 8.55, "processing_fee": "₹ 3,500"}, '
                                '{"bank_name": "SBI", "interest_rate": 8.30, "processing_fee": "₹ 2,000"} '
                                ']}'
                            )
                        }
                    }
                ]
            },
        )
    )
    tavily_results = [
        {"title": "HDFC Home Loan", "content": "Rates and fees", "url": "https://hdfc.com"},
        {"title": "SBI Home Loan", "content": "Rates and fees", "url": "https://sbi.co.in"},
    ]
    out = extract_loan_offers_from_tavily(tavily_results)
    assert isinstance(out, list)
    assert any(o.get("bank_name") == "HDFC" for o in out)


@respx.mock
def test_extract_loan_offers_bad_json(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {"content": "not json"}}]})
    )
    with pytest.raises(APIError):
        extract_loan_offers_from_tavily([])


@respx.mock
def test_extract_loan_offers_rate_limit(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=httpx.Response(429, json={"error": {"message": "rate limit"}})
    )
    with pytest.raises(RateLimitError):
        extract_loan_offers_from_tavily([])