import reflex as rx
from app.states.state import PropMateState
from app.states.loan_state import LoanState
from app.states.chat_state import ChatState


def metric(label: str, value: rx.Var, icon: str) -> rx.Component:
    return rx.el.div(
        rx.icon(icon, class_name="h-4 w-4 text-teal-700"),
        rx.el.span(label, class_name="text-xs text-gray-600"),
        rx.el.span(value, class_name="text-sm font-medium text-gray-900"),
        class_name="flex items-center gap-2 px-3 py-1 rounded-full bg-gray-100",
    )


def status_bar() -> rx.Component:
    return rx.el.footer(
        rx.el.div(
            metric("Analysis", PropMateState.last_analysis_duration_ms.to_string() + " ms", "activity"),
            metric("Web", PropMateState.last_web_fetch_duration_ms.to_string() + " ms", "globe"),
            metric("Loans", LoanState.last_fetch_duration_ms.to_string() + " ms", "landmark"),
            metric("Chat", ChatState.last_chat_duration_ms.to_string() + " ms", "message-square"),
            class_name="flex flex-wrap gap-2 items-center",
        ),
        aria_label="Performance metrics",
        class_name=(
            "sticky bottom-0 w-full bg-white/90 backdrop-blur border-t px-4 py-2 "
            "shadow-sm motion-reduce:transition-none transition-colors duration-200"
        ),
    )