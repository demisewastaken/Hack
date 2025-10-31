import reflex as rx
from typing import TypedDict, List
import time
from app.services.tavily_client import search_web
from app.services.openai_client import extract_loan_offers_from_tavily
from app.services.errors import ConfigError, AuthenticationError, RateLimitError, APIError


class LoanOffer(TypedDict):
    bank_name: str
    interest_rate: str
    processing_fee: str


class LoanState(rx.State):
    loan_amount: int = 1000000
    tenure_years: int = 20
    interest_rate: float = 8.0
    is_fetching_loans: bool = False
    loan_offers: List[LoanOffer] = []
    last_fetch_duration_ms: int = 0

    @rx.var
    def tenure_months(self) -> int:
        return int(self.tenure_years * 12)

    @rx.var
    def monthly_interest_rate(self) -> float:
        return float(self.interest_rate) / 12.0 / 100.0

    @rx.var
    def emi(self) -> str:
        P = float(self.loan_amount or 0)
        r = float(self.monthly_interest_rate)
        n = int(self.tenure_months or 1)
        if r == 0 or n == 0:
            emi_val = P / max(n, 1)
        else:
            emi_val = P * r * (1 + r) ** n / ((1 + r) ** n - 1)
        return f"₹ {emi_val:,.0f}"

    @rx.var
    def total_payment(self) -> str:
        P = float(self.loan_amount or 0)
        r = float(self.monthly_interest_rate)
        n = int(self.tenure_months or 1)
        if r == 0 or n == 0:
            total = P
        else:
            emi_val = P * r * (1 + r) ** n / ((1 + r) ** n - 1)
            total = emi_val * n
        return f"₹ {total:,.0f}"

    @rx.var
    def total_interest(self) -> str:
        P = float(self.loan_amount or 0)
        total = self._parse_currency(self.total_payment)
        interest = max(total - P, 0)
        return f"₹ {interest:,.0f}"

    def _parse_currency(self, currency_str: str) -> float:
        try:
            return float(currency_str.replace("₹", "").replace(",", "").strip())
        except Exception:
            return 0.0

    def set_loan_amount(self, value: float):
        try:
            amt = float(value)
        except Exception:
            amt = 0.0
        # Clamp to UI slider bounds.
        amt = max(100000.0, min(amt, 20000000.0))
        self.loan_amount = int(amt)

    def set_tenure_years(self, value: float):
        try:
            yrs = float(value)
        except Exception:
            yrs = 0.0
        yrs = max(1.0, min(yrs, 30.0))
        self.tenure_years = int(yrs)

    def set_interest_rate(self, value: float):
        try:
            rate = float(value)
        except Exception:
            rate = 0.0
        rate = max(5.0, min(rate, 15.0))
        self.interest_rate = rate

    @rx.event(background=True)
    async def fetch_loan_offers(self):
        t0 = time.perf_counter()
        async with self:
            self.is_fetching_loans = True
            self.loan_offers = []

        # Query common Indian banks for home loan rates.
        query = (
            "latest home loan interest rates from HDFC, SBI, ICICI, Axis Bank in India"
        )

        offers: List[LoanOffer] = []
        try:
            tavily_results = search_web(query, max_results=5)
            extracted = extract_loan_offers_from_tavily(tavily_results)
            # Normalize into LoanOffer TypedDict shape.
            for o in extracted:
                offers.append(
                    {
                        "bank_name": o.get("bank_name", "").strip(),
                        "interest_rate": o.get("interest_rate", "").strip(),
                        "processing_fee": o.get("processing_fee", "").strip(),
                    }
                )
        except ConfigError:
            # Missing keys; keep empty offers.
            pass
        except AuthenticationError:
            pass
        except RateLimitError:
            pass
        except APIError:
            pass
        except Exception:
            # Any unexpected error should not crash UI.
            pass

        async with self:
            self.loan_offers = offers
            t1 = time.perf_counter()
            self.last_fetch_duration_ms = int((t1 - t0) * 1000)
            self.is_fetching_loans = False

    def on_load_calculate(self):
        pass