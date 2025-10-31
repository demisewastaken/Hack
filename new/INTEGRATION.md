# API Integration Guide

This application integrates two backend services using server-side environment variables loaded from `new/.env`:

- OpenAI (chat replies)
- Tavily (live web search for property analysis)

All API keys are loaded on the server only and are never exposed to client-side code.

## Environment Variables

Set these in `new/.env`:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Optional model name; defaults to a sensible value
- `TAVILY_API_KEY`: Your Tavily API key (required)
- `TAVILY_BASE_URL`: Optional; defaults to `https://api.tavily.com`

## Where Keys Are Loaded

- `app/services/settings.py` loads `.env` via `python-dotenv` and provides getters.
- Keys are used by `app/services/openai_client.py` and `app/services/tavily_client.py`.
- Keys are never transmitted to the frontend.

## API Endpoints

- OpenAI Chat Completions: `https://api.openai.com/v1/chat/completions`
- Tavily Search: `https://api.tavily.com/search`  
  Authorization header: `Authorization: Bearer tvly-<YOUR_API_KEY>`

## Error Handling

The clients raise typed exceptions:

- `ConfigError`: Missing required environment variable
- `AuthenticationError`: 401/403 authentication failures
- `RateLimitError`: 429 rate limit exceeded
- `APIError`: Timeout or other HTTP errors

States catch these errors and degrade gracefully:

- Chat falls back to a helpful message when errors occur.
- Property analysis continues without web data if Tavily fails.

## Testing

Run tests from the `new/` directory:

```
python3 -m pip install -r requirements.txt
pytest -q
```

Tests cover:

- Env loading and required keys
- Successful API authentication and data retrieval (mocked)
- Error handling scenarios: missing key, auth failure, timeouts/rate limits

## Security Practices

- Keys are loaded server-side and never appear in client bundles.
- Requests include `Authorization: Bearer ...` headers only from backend.
- Avoid logging raw keys. Do not put keys in `rxconfig.py` or client code.

## Setup Steps

1. Put your keys into `new/.env`.
2. Install dependencies: `python3 -m pip install -r requirements.txt`.
3. Start the app: `reflex run` from `new/`.
4. Open `http://localhost:3000/`.

## Notes

- To adjust the OpenAI model, set `OPENAI_MODEL` in `.env`.
- Tavily parameters can be tuned in `tavily_client.search_web`.

## Loan Workflow

- Background fetching of live loan offers is implemented in `app/states/loan_state.py` via `fetch_loan_offers`.
- Offer extraction uses `app/services/openai_client.py: extract_loan_offers_from_tavily`, returning a list of `{bank_name, interest_rate, processing_fee}`.
- UI rendering and slider inputs are defined in `app/components/loan_calculator.py` with throttled change events and accessible loading states.

### Validate End-to-End

- Start the app and open `http://localhost:3001/`.
- Navigate to the Loans page.
- Adjust sliders for `Loan Amount`, `Tenure (years)`, and `Interest Rate`.
- Click `Fetch Best Offers` and observe live offers populate from HDFC/SBI/ICICI/Axis when available.
- Status bar shows `last_fetch_duration_ms` for performance tracking.

## Fixes Summary

- Event handler types aligned with slider expectations:
  - `LoanState.set_loan_amount` and `set_tenure_years` now accept `float` and clamp to valid ranges.
  - `LoanState.set_interest_rate` clamps between `5.0` and `15.0`.
- Robust extractor and error handling:
  - Added `extract_loan_offers_from_tavily` using OpenAI with strict JSON response.
  - Normalizes parsed fields and raises typed errors on failures.
- Developer experience:
  - Resolved duplicate dev servers to avoid Bun link conflicts.
  - Added tests for extractor success, bad JSON, and rate limits.

## Troubleshooting

- If offers appear empty, confirm `OPENAI_API_KEY` and `TAVILY_API_KEY` are set in `new/.env`.
- If rate-limited, retry later or add caching around `fetch_loan_offers`.
- If Bun shows `EEXIST` during frontend install, ensure only one dev server instance is running.