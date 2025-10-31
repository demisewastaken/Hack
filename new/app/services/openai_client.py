from __future__ import annotations

import httpx

from .errors import APIError, AuthenticationError, RateLimitError, ConfigError
from .settings import get_openai_api_key, get_openai_model


def generate_chat_reply(query: str, history: list[dict] | None = None) -> str:
    """Generate a reply using OpenAI Chat Completions.

    Args:
        query: User query string.
        history: Optional prior messages, each with keys 'role' and 'content'.

    Returns:
        Assistant text reply.

    Raises:
        ConfigError, AuthenticationError, RateLimitError, APIError
    """
    api_key = get_openai_api_key(required=True)
    model = get_openai_model()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    messages: list[dict] = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant for property pricing, listings, and loans. "
                "Answer succinctly and include actionable guidance."
            ),
        }
    ]
    if history:
        messages.extend(history)
    if query:
        messages.append({"role": "user", "content": query})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
    }

    try:
        with httpx.Client(timeout=httpx.Timeout(15.0)) as client:
            resp = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            if resp.status_code == 401 or resp.status_code == 403:
                raise AuthenticationError("OpenAI authentication failed.")
            if resp.status_code == 429:
                raise RateLimitError("OpenAI rate limit exceeded.")
            resp.raise_for_status()
            data = resp.json()
    except httpx.TimeoutException as e:
        raise APIError("OpenAI request timed out.") from e
    except httpx.HTTPStatusError as e:
        raise APIError(f"OpenAI HTTP error: {e.response.status_code}") from e
    except httpx.RequestError as e:
        raise APIError(f"OpenAI request error: {e}") from e

    try:
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        raise APIError("Unexpected OpenAI response format.")


def extract_loan_offers_from_tavily(tavily_results: list[dict]) -> list[dict]:
    """Use OpenAI to extract structured loan offers from Tavily results.

    Returns a list of {bank_name, interest_rate, processing_fee} dicts.
    """
    api_key = get_openai_api_key(required=True)
    model = get_openai_model()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    system_prompt = (
        "You are a financial data extractor. Based on the provided search results "
        "about home loan interest rates in India, extract the bank name, interest "
        "rate, and processing fee for each mentioned bank (e.g., HDFC, SBI, ICICI, Axis Bank).\n\n"
        "Respond ONLY with a JSON object containing a single key 'loan_offers', which is a list of objects. "
        "Each object must have these keys: 'bank_name', 'interest_rate', 'processing_fee'."
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Tavily Search Results: {tavily_results}"},
        ],
        # Prefer JSON format when supported.
        "response_format": {"type": "json_object"},
        "temperature": 0,
    }

    try:
        with httpx.Client(timeout=httpx.Timeout(20.0)) as client:
            resp = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            if resp.status_code == 401 or resp.status_code == 403:
                raise AuthenticationError("OpenAI authentication failed.")
            if resp.status_code == 429:
                raise RateLimitError("OpenAI rate limit exceeded.")
            resp.raise_for_status()
            data = resp.json()
    except httpx.TimeoutException as e:
        raise APIError("OpenAI request timed out.") from e
    except httpx.HTTPStatusError as e:
        raise APIError(f"OpenAI HTTP error: {e.response.status_code}") from e
    except httpx.RequestError as e:
        raise APIError(f"OpenAI request error: {e}") from e

    try:
        content = data["choices"][0]["message"]["content"].strip()
    except Exception:
        raise APIError("Unexpected OpenAI response format.")

    # Parse JSON response with fallback.
    try:
        import json

        parsed = json.loads(content)
        offers = parsed.get("loan_offers") or []
        if isinstance(offers, list):
            normalized: list[dict] = []
            for o in offers:
                normalized.append(
                    {
                        "bank_name": str(o.get("bank_name", "")).strip(),
                        "interest_rate": str(o.get("interest_rate", "")).strip(),
                        "processing_fee": str(o.get("processing_fee", "")).strip(),
                    }
                )
            return normalized
        return []
    except Exception as e:
        # Fallback: return empty to allow UI to degrade gracefully.
        raise APIError("Failed to parse loan offers JSON.") from e