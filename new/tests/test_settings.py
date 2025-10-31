import os
import pytest

from app.services import settings
from app.services.errors import ConfigError


def test_get_openai_api_key_required(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ConfigError):
        settings.get_openai_api_key(required=True)


def test_get_openai_api_key_present(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    assert settings.get_openai_api_key(required=True) == "sk-test"


def test_get_tavily_base_url_default(monkeypatch):
    monkeypatch.delenv("TAVILY_BASE_URL", raising=False)
    assert settings.get_tavily_base_url() == "https://api.tavily.com"