import reflex as rx
from app.components.sidebar import sidebar
from app.components.property_form import property_form
from app.components.analysis_card import analysis_card
from app.components.loan_calculator import loan_calculator_page
from app.components.chat_interface import chat_page
from app.components.status_bar import status_bar
from app.states.state import PropMateState
from app.states.loan_state import LoanState
from app.states.chat_state import ChatState


def index() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.main(
            rx.el.div(
                rx.el.h1(
                    "PropMate AI",
                    class_name="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl md:text-6xl",
                ),
                rx.el.p(
                    "Your AI partner that predicts property worth, finds live listings, and plans your loan ",
                    class_name="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl",
                ),
                class_name="text-center",
            ),
            property_form(),
            rx.el.div(
                rx.el.h3(
                    "Analysis History",
                    class_name="text-2xl font-bold tracking-tight text-gray-900",
                ),
                rx.foreach(PropMateState.property_database, analysis_card),
                class_name="space-y-4",
            ),
            class_name=(
                "flex flex-1 flex-col gap-4 p-4 md:gap-8 md:p-6 "
                "transition-all duration-200 ease-out motion-reduce:transition-none"
            ),
        ),
        status_bar(),
        class_name=(
            "grid min-h-screen w-full md:grid-cols-[220px_1fr] lg:grid-cols-[280px_1fr] "
            "font-['Inter'] bg-white"
        ),
    )


def loans() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.main(
            loan_calculator_page(),
            class_name=(
                "flex flex-1 flex-col gap-4 p-4 md:gap-8 md:p-6 "
                "transition-all duration-200 ease-out motion-reduce:transition-none"
            ),
        ),
        status_bar(),
        class_name=(
            "grid min-h-screen w-full md:grid-cols-[220px_1fr] lg:grid-cols-[280px_1fr] "
            "font-['Inter'] bg-white"
        ),
    )


def chat() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.main(
            chat_page(),
            class_name=(
                "flex flex-1 flex-col h-[90vh] transition-all duration-200 ease-out "
                "motion-reduce:transition-none"
            ),
        ),
        status_bar(),
        class_name=(
            "grid min-h-screen w-full md:grid-cols-[220px_1fr] lg:grid-cols-[280px_1fr] "
            "font-['Inter'] bg-white"
        ),
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, on_load=LoanState.on_load_calculate)
app.add_page(loans, on_load=LoanState.on_load_calculate)
app.add_page(chat, on_load=ChatState.on_page_load)