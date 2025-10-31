import reflex as rx
from app.states.state import PropMateState


def form_field(
    label: str,
    placeholder: str,
    value: rx.Var,
    on_change: rx.event.EventHandler,
    type: str = "text",
) -> rx.Component:
    input_id = f"field-{label.lower().replace(' ', '-')}"
    return rx.el.div(
        rx.el.label(
            label,
            class_name="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70",
        ),
        rx.el.input(
            placeholder=placeholder,
            on_change=on_change,
            type=type,
            id=input_id,
            aria_label=label,
            inputmode="numeric" if type == "number" else None,
            class_name="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
            default_value=value,
        ),
        class_name="grid gap-2",
    )


def property_form() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3("Property Details", class_name="text-lg font-semibold"),
            rx.el.p(
                "Enter the details of the property you want to analyze.",
                class_name="text-sm text-gray-500",
            ),
            class_name="space-y-1",
        ),
        rx.el.form(
            rx.el.div(
                form_field(
                    "Area (sqft)",
                    "e.g., 1200",
                    PropMateState.area,
                    PropMateState.set_area,
                    type="number",
                ),
                form_field(
                    "Bedrooms",
                    "e.g., 3",
                    PropMateState.bedrooms,
                    PropMateState.set_bedrooms,
                    type="number",
                ),
                form_field(
                    "Bathrooms",
                    "e.g., 2",
                    PropMateState.bathrooms,
                    PropMateState.set_bathrooms,
                    type="number",
                ),
                form_field(
                    "Floor",
                    "e.g., 5",
                    PropMateState.floor,
                    PropMateState.set_floor,
                    type="number",
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4",
            ),
            form_field(
                "Location",
                "e.g., Koramangala, Bangalore",
                PropMateState.location,
                PropMateState.set_location,
            ),
            rx.el.button(
                rx.cond(
                    PropMateState.is_analyzing,
                    rx.el.div(
                        rx.spinner(class_name="h-4 w-4 mr-2", aria_hidden=True),
                        "Analyzing...",
                        class_name="flex items-center",
                    ),
                    "Analyze Property",
                ),
                type="button",
                on_click=PropMateState.analyze_property,
                disabled=PropMateState.is_analyzing,
                aria_busy=PropMateState.is_analyzing,
                class_name=(
                    "w-full bg-teal-600 text-white font-semibold py-2 px-4 rounded-lg "
                    "hover:bg-teal-700 transition-colors duration-200 motion-reduce:transition-none "
                    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 disabled:bg-gray-400 mt-4"
                ),
            ),
            class_name="space-y-4",
        ),
        class_name=(
            "p-6 bg-white rounded-lg shadow-sm border border-gray-200 "
            "transition-shadow duration-200 motion-reduce:transition-none"
        ),
    )