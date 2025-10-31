import pytest
import respx
import httpx

from app.services.tavily_client import search_web
from app.services.errors import AuthenticationError, RateLimitError, ConfigError


@respx.mock
def test_tavily_search_success(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test")
    respx.post("https://api.tavily.com/search").mock(
        return_value=httpx.Response(
            200,
            json={
                "results": [
                    {
                        "title": "Listing A",
                        "content": "Nice place",
                        "url": "https://example.com/a",
                    }
                ]
            },
        )
    )
    out = search_web("3BHK in Pune", max_results=3)
    assert len(out) == 1
    assert out[0]["url"] == "https://example.com/a"


@respx.mock
def test_tavily_auth_error(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test")
    respx.post("https://api.tavily.com/search").mock(
        return_value=httpx.Response(401, json={"error": "bad key"})
    )
    with pytest.raises(AuthenticationError):
        search_web("test")


@respx.mock
def test_tavily_rate_limit(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test")
    respx.post("https://api.tavily.com/search").mock(
        return_value=httpx.Response(429, json={"error": "rate limit"})
    )
    with pytest.raises(RateLimitError):
        search_web("test")


def test_tavily_missing_key(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    with pytest.raises(ConfigError):
        search_web("test")