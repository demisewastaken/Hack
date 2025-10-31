from __future__ import annotations

import httpx

from .errors import APIError, AuthenticationError, RateLimitError
from .settings import get_tavily_api_key, get_tavily_base_url


def search_web(query: str, max_results: int = 6) -> list[dict]:
    """Search the web using Tavily and return simplified results.

    Each result has 'title', 'content', and 'url'.
    """
    api_key = get_tavily_api_key(required=True)
    base_url = get_tavily_base_url().rstrip("/")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "query": query,
        "max_results": max(1, min(max_results, 20)),
        "search_depth": "basic",
        "include_answer": False,
        "include_raw_content": False,
    }

    try:
        with httpx.Client(timeout=httpx.Timeout(15.0)) as client:
            resp = client.post(f"{base_url}/search", headers=headers, json=payload)
            if resp.status_code == 401 or resp.status_code == 403:
                raise AuthenticationError("Tavily authentication failed.")
            if resp.status_code == 429:
                raise RateLimitError("Tavily rate limit exceeded.")
            resp.raise_for_status()
            data = resp.json()
    except httpx.TimeoutException as e:
        raise APIError("Tavily request timed out.") from e
    except httpx.HTTPStatusError as e:
        raise APIError(f"Tavily HTTP error: {e.response.status_code}") from e
    except httpx.RequestError as e:
        raise APIError(f"Tavily request error: {e}") from e

    out: list[dict] = []
    for item in (data.get("results") or []):
        out.append(
            {
                "title": item.get("title") or item.get("source") or "",
                "content": item.get("content") or item.get("snippet") or "",
                "url": item.get("url") or "",
            }
        )
    return out