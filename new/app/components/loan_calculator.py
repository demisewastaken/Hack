import reflex as rx
from app.states.loan_state import LoanState, LoanOffer


def slider_field(
    label: str,
    value: rx.Var,
    on_change: rx.event.EventHandler,
    min_val: int,
    max_val: int,
    step: int,
) -> rx.Component:
    return rx.el.div(
        rx.el.label(label, f" ( {value} )", class_name="font-medium text-gray-700"),
        rx.el.input(
            type="range",
            key=label,
            default_value=value,
            on_change=on_change.throttle(100),
            min=min_val,
            max=max_val,
            step=step,
            aria_valuemin=min_val,
            aria_valuemax=max_val,
            aria_valuenow=value,
            class_name=(
                "w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-teal-600 "
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500"
            ),
        ),
        class_name="space-y-2",
    )


def emi_summary_card(label: str, value: rx.Var, bg_color: str) -> rx.Component:
    return rx.el.div(
        rx.el.p(label, class_name="text-sm font-medium text-gray-600"),
        rx.el.p(value, class_name="text-2xl font-bold text-gray-900"),
        class_name=f"p-4 rounded-lg {bg_color} text-center",
    )


def loan_offer_card(offer: LoanOffer) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                offer["bank_name"], class_name="font-semibold text-lg text-gray-900"
            ),
            class_name="flex items-center gap-2",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p("Interest Rate", class_name="text-xs text-gray-500"),
                rx.el.p(offer["interest_rate"], class_name="font-medium text-teal-700"),
                class_name="text-center",
            ),
            rx.el.div(
                rx.el.p("Processing Fee", class_name="text-xs text-gray-500"),
                rx.el.p(
                    offer["processing_fee"], class_name="font-medium text-gray-700"
                ),
                class_name="text-center",
            ),
            class_name="grid grid-cols-2 gap-4 mt-2 pt-2 border-t",
        ),
        class_name="p-4 bg-white rounded-lg border border-gray-200 shadow-sm space-y-2",
    )


def loan_calculator_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "Loan & EMI Calculator", class_name="text-3xl font-bold text-gray-900"
            ),
            rx.el.p(
                "Estimate your Equated Monthly Installment (EMI) and find the best loan offers.",
                class_name="text-gray-600 mt-1",
            ),
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h3("EMI Calculator", class_name="text-xl font-semibold mb-4"),
                rx.el.div(
                    slider_field(
                        "Loan Amount (₹)",
                        LoanState.loan_amount,
                        LoanState.set_loan_amount,
                        100000,
                        20000000,
                        100000,
                    ),
                    slider_field(
                        "Loan Tenure (Years)",
                        LoanState.tenure_years,
                        LoanState.set_tenure_years,
                        1,
                        30,
                        1,
                    ),
                    slider_field(
                        "Interest Rate (%)",
                        LoanState.interest_rate,
                        LoanState.set_interest_rate,
                        5.0,
                        15.0,
                        0.1,
                    ),
                    class_name="space-y-6",
                ),
                rx.el.div(
                    emi_summary_card("Monthly EMI", LoanState.emi, "bg-teal-100"),
                    emi_summary_card(
                        "Total Interest", LoanState.total_interest, "bg-orange-100"
                    ),
                    emi_summary_card(
                        "Total Payment", LoanState.total_payment, "bg-blue-100"
                    ),
                    class_name="grid md:grid-cols-3 gap-4 mt-8",
                ),
                class_name=(
                    "p-6 bg-white rounded-lg shadow-sm border "
                    "transition-shadow duration-200 motion-reduce:transition-none"
                ),
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        "Live Home Loan Offers", class_name="text-xl font-semibold"
                    ),
                        rx.el.button(
                            rx.cond(
                                LoanState.is_fetching_loans,
                                rx.el.div(
                                    rx.spinner(class_name="h-4 w-4 mr-2", aria_hidden=True),
                                    "Fetching...",
                                    class_name="flex items-center",
                                ),
                                "Fetch Best Offers",
                            ),
                            on_click=LoanState.fetch_loan_offers,
                            disabled=LoanState.is_fetching_loans,
                            aria_busy=LoanState.is_fetching_loans,
                            class_name=(
                                "bg-teal-600 text-white font-semibold py-2 px-4 rounded-lg "
                                "hover:bg-teal-700 transition-colors duration-200 motion-reduce:transition-none "
                                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 disabled:bg-gray-400"
                            ),
                        ),
                    class_name="flex justify-between items-center mb-4",
                ),
                rx.cond(
                    LoanState.is_fetching_loans,
                    rx.el.div(
                        rx.spinner(class_name="h-8 w-8 text-teal-600", aria_hidden=True),
                        class_name="flex justify-center p-8",
                        role="status",
                    ),
                    rx.cond(
                        LoanState.loan_offers.length() > 0,
                        rx.el.div(
                            rx.foreach(LoanState.loan_offers, loan_offer_card),
                            class_name="grid md:grid-cols-2 lg:grid-cols-4 gap-4",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Click 'Fetch Best Offers' to see live loan rates from top banks.",
                                class_name="text-gray-500",
                            ),
                            class_name="text-center p-8 border-2 border-dashed rounded-lg",
                        ),
                    ),
                ),
                    class_name=(
                        "p-6 bg-white rounded-lg shadow-sm border "
                        "transition-shadow duration-200 motion-reduce:transition-none"
                    ),
            ),
            class_name="grid lg:grid-cols-2 gap-8",
        ),
        class_name="space-y-8",
    )