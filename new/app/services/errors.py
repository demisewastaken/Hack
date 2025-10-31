class ConfigError(Exception):
    """Raised when required configuration (e.g., API keys) is missing."""


class AuthenticationError(Exception):
    """Raised when authentication with an external API fails (401/403)."""


class RateLimitError(Exception):
    """Raised when an external API rate limit is exceeded (429)."""


class APIError(Exception):
    """Raised when an external API request fails for other reasons."""