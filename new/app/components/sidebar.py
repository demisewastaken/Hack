import reflex as rx
from app.states.state import PropMateState


def nav_item(icon: str, text: str, href: str, is_active: rx.Var[bool]) -> rx.Component:
    return rx.el.a(
        rx.icon(icon, class_name="h-5 w-5"),
        rx.el.span(text),
        href=href,
        aria_current=rx.cond(is_active, "page", ""),
        aria_label=text,
        class_name=rx.cond(
            is_active,
            "flex items-center gap-3 rounded-lg px-3 py-2 bg-gray-200 text-gray-900 transition-colors duration-200 hover:text-gray-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500",
            "flex items-center gap-3 rounded-lg px-3 py-2 text-gray-500 transition-colors duration-200 hover:text-gray-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500",
        ),
    )


def sidebar() -> rx.Component:
    current_page = PropMateState.router.page.path
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    rx.icon("home", class_name="h-8 w-8 text-teal-600"),
                    rx.el.span("PropMate AI", class_name="sr-only"),
                    href="/",
                    class_name="flex items-center gap-2 font-semibold",
                ),
                class_name="flex h-16 items-center border-b px-6",
            ),
            rx.el.div(
                rx.el.nav(
                    nav_item(
                        icon="bar-chart-2",
                        text="Analyze",
                        href="/",
                        is_active=(current_page == "/") | (current_page == ""),
                    ),
                    nav_item(
                        icon="landmark",
                        text="Loans",
                        href="/loans",
                        is_active=current_page == "/loans",
                    ),
                    nav_item(
                        icon="message-square",
                        text="Chat",
                        href="/chat",
                        is_active=current_page == "/chat",
                    ),
                    class_name="grid items-start px-4 text-sm font-medium gap-1",
                ),
                class_name="flex-1 overflow-auto py-2",
            ),
        ),
        class_name="hidden border-r bg-gray-100/40 md:block",
    )