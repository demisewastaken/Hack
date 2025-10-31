import reflex as rx
from typing import List
from app.states.state import Message
from app.services.openai_client import generate_chat_reply
from app.services.errors import (
    APIError,
    AuthenticationError,
    RateLimitError,
    ConfigError,
)
import time


class ChatState(rx.State):
    messages: List[Message] = []
    is_processing: bool = False
    last_chat_duration_ms: int = 0

    def on_page_load(self):
        if not self.messages:
            self.messages.append(
                {
                    "role": "assistant",
                    "content": "Hi! Ask me about property pricing, listings, or loans.",
                }
            )

    def send_quick_question(self, question: str):
        self.messages.append({"role": "user", "content": question})
        self._respond(question)

    def process_query(self, form_data: dict):
        query = form_data.get("query", "") if isinstance(form_data, dict) else ""
        if query:
            self.messages.append({"role": "user", "content": query})
        self._respond(query)

    def _respond(self, query: str):
        self.is_processing = True
        t0 = time.perf_counter()
        try:
            reply = generate_chat_reply(query, history=self.messages)
        except ConfigError:
            reply = (
                "API key not configured. Set OPENAI_API_KEY in the server environment."
            )
        except AuthenticationError:
            reply = "Authentication failed. Please verify your API key is valid."
        except RateLimitError:
            reply = (
                "Rate limit exceeded. Please wait a moment before trying again."
            )
        except APIError as e:
            reply = f"Service error: {e}"
        except Exception:
            reply = "Unexpected error while processing your request."

        self.messages.append({"role": "assistant", "content": reply})
        t1 = time.perf_counter()
        self.last_chat_duration_ms = int((t1 - t0) * 1000)
        self.is_processing = False