import reflex as rx
from typing import TypedDict, List
import time
from app.services.tavily_client import search_web
from app.services.errors import APIError, AuthenticationError, RateLimitError, ConfigError


class Property(TypedDict):
    location: str
    area: int
    bedrooms: int
    bathrooms: int
    floor: int
    investment_score: int
    area_growth: str
    estimated_value: str
    ai_insights: str
    market_insights: str
    tavily_results: List[dict]


class Message(TypedDict):
    role: str
    content: str


class PropMateState(rx.State):
    area: int = 0
    bedrooms: int = 0
    bathrooms: int = 0
    floor: int = 0
    location: str = ""
    is_analyzing: bool = False
    property_database: List[Property] = []
    last_analysis_duration_ms: int = 0
    last_web_fetch_duration_ms: int = 0
    analysis_count: int = 0

    def set_area(self, value: int):
        try:
            self.area = int(value)
        except Exception:
            self.area = 0

    def set_bedrooms(self, value: int):
        try:
            self.bedrooms = int(value)
        except Exception:
            self.bedrooms = 0

    def set_bathrooms(self, value: int):
        try:
            self.bathrooms = int(value)
        except Exception:
            self.bathrooms = 0

    def set_floor(self, value: int):
        try:
            self.floor = int(value)
        except Exception:
            self.floor = 0

    def set_location(self, value: str):
        self.location = value or ""

    def analyze_property(self):
        self.is_analyzing = True
        t0 = time.perf_counter()
        base_rate = 7500
        adjustment = 0
        adjustment += max(self.bedrooms - 2, 0) * 500
        adjustment += max(self.bathrooms - 2, 0) * 400
        adjustment += max(self.floor - 1, 0) * 100
        rate = max(base_rate + adjustment, 0)
        predicted = int(max(self.area, 0) * rate)

        ai_insights = (
            "Based on the inputs, this property has a reasonable valuation. "
            "Consider verifying locality amenities, recent sales, and builder reputation."
        )
        market_insights = (
            "Recent market trends indicate stable prices with moderate demand. "
            "Negotiation margin could be around 3–7% depending on competition."
        )

        investment_score = min(max(int(predicted / 100000), 0), 100)
        area_growth = "Up 4.2% YoY"
        estimated_value = f"₹ {predicted:,.0f}"

        new_entry: Property = {
            "location": self.location or "",
            "area": int(self.area or 0),
            "bedrooms": int(self.bedrooms or 0),
            "bathrooms": int(self.bathrooms or 0),
            "floor": int(self.floor or 0),
            "investment_score": investment_score,
            "area_growth": area_growth,
            "estimated_value": estimated_value,
            "ai_insights": ai_insights,
            "market_insights": market_insights,
            "tavily_results": [],
        }
        # Fetch live web results via Tavily.
        tw0 = time.perf_counter()
        try:
            query = (
                f"{new_entry['bedrooms']} BHK in {new_entry['location']} around {new_entry['estimated_value']}"
            )
            results = search_web(query, max_results=6)
            new_entry["tavily_results"] = results
        except ConfigError:
            # Keep running without web data.
            pass
        except AuthenticationError:
            pass
        except RateLimitError:
            pass
        except APIError:
            pass
        tw1 = time.perf_counter()
        self.last_web_fetch_duration_ms = int((tw1 - tw0) * 1000)

        self.property_database = [new_entry] + list(self.property_database)
        t1 = time.perf_counter()
        self.last_analysis_duration_ms = int((t1 - t0) * 1000)
        self.analysis_count += 1
        self.is_analyzing = False