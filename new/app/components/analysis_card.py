import reflex as rx
from app.states.state import Property


def info_badge(icon: str, text: rx.Var, bg_color: str) -> rx.Component:
    return rx.el.div(
        rx.icon(icon, class_name="h-5 w-5"),
        rx.el.span(text),
        class_name=f"flex items-center gap-2 rounded-full px-3 py-1 text-sm font-medium {bg_color} w-fit",
    )


def tavily_result_card(result: dict) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.el.h5(result["title"], class_name="font-semibold text-blue-600"),
            rx.el.p(result["content"], class_name="text-xs text-gray-600 line-clamp-2"),
            rx.el.p(
                rx.el.span("Source: "),
                result["url"],
                class_name="text-xs text-gray-400 truncate",
            ),
            class_name="space-y-1",
        ),
        href=result["url"],
        target="_blank",
        rel="noopener noreferrer",
        class_name=(
            "block p-2 border rounded-lg hover:bg-gray-50 transition-colors duration-200 "
            "motion-reduce:transition-none"
        ),
    )


def analysis_card(property: Property) -> rx.Component:
    score_color = rx.cond(
        property["investment_score"] > 75,
        "bg-green-100 text-green-800",
        rx.cond(
            property["investment_score"] > 50,
            "bg-yellow-100 text-yellow-800",
            "bg-red-100 text-red-800",
        ),
    )
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h4(
                    property["location"],
                    class_name="text-lg font-semibold text-gray-900",
                ),
                rx.el.p(
                    f"{property['bedrooms']} BHK | {property['bathrooms']} Bath | {property['area']} sqft | Floor: {property['floor']}",
                    class_name="text-sm text-gray-500",
                ),
                class_name="flex-1",
            ),
            rx.el.div(
                info_badge(
                    "activity",
                    rx.el.span("Score: ", property["investment_score"].to_string()),
                    score_color,
                ),
                info_badge(
                    "trending-up",
                    property["area_growth"],
                    "bg-indigo-100 text-indigo-800",
                ),
                info_badge(
                    "banknote", property["estimated_value"], "bg-blue-100 text-blue-800"
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="flex flex-wrap items-start justify-between gap-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h5(
                    "AI Insights & Negotiation Advice",
                    class_name="font-semibold text-gray-800",
                ),
                rx.el.p(property["ai_insights"], class_name="text-sm text-gray-600"),
                class_name="p-4 bg-teal-50/50 border border-teal-200 rounded-lg",
            ),
            rx.el.div(
                rx.el.h5("Market Insights", class_name="font-semibold text-gray-800"),
                rx.el.p(
                    property["market_insights"], class_name="text-sm text-gray-600"
                ),
                class_name="p-4 bg-gray-50 border rounded-lg",
            ),
            class_name="grid md:grid-cols-2 gap-4 mt-4",
        ),
        rx.cond(
            property["tavily_results"].length() > 0,
            rx.el.div(
                rx.el.h5(
                    "Live Web Data", class_name="font-semibold text-gray-800 mt-4 mb-2"
                ),
                rx.el.div(
                    rx.foreach(property["tavily_results"], tavily_result_card),
                    class_name="grid md:grid-cols-2 lg:grid-cols-3 gap-2",
                ),
                aria_label="Live web results",
            ),
        ),
        role="article",
        class_name=(
            "p-4 bg-white rounded-lg shadow-sm border border-gray-200 space-y-4 "
            "transition-shadow duration-200 motion-reduce:transition-none"
        ),
    )