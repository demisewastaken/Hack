from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

# Load .env once at import. Keys remain server-side only.
load_dotenv(_ENV_PATH, override=False)


def _get(name: str, default: Optional[str] = None, required: bool = False) -> str:
    val = os.getenv(name, default)
    if required and not val:
        from .errors import ConfigError

        raise ConfigError(f"Missing required environment variable: {name}")
    return val or ""


def get_openai_api_key(required: bool = True) -> str:
    return _get("OPENAI_API_KEY", required=required)


def get_openai_model() -> str:
    # Allow override; otherwise use a sensible default.
    return _get("OPENAI_MODEL", default="gpt-4o-mini", required=False)


def get_tavily_api_key(required: bool = True) -> str:
    return _get("TAVILY_API_KEY", required=required)


def get_tavily_base_url() -> str:
    # Default to official base URL.
    return _get("TAVILY_BASE_URL", default="https://api.tavily.com", required=False)