import reflex as rx
from app.states.state import Message
from app.states.chat_state import ChatState


def message_bubble(message: Message) -> rx.Component:
    is_user = message.get("role") == "user"
    return rx.el.div(
        rx.el.div(
            rx.markdown(message.get("content", ""), class_name="prose text-sm"),
            class_name=rx.cond(
                is_user,
                "p-3 rounded-l-lg rounded-br-lg bg-teal-500 text-white",
                "p-3 rounded-r-lg rounded-bl-lg bg-gray-200 text-gray-800",
            ),
        ),
        class_name=rx.cond(
            is_user, "flex justify-end w-full", "flex justify-start w-full"
        ),
    )


def quick_question_button(question: str) -> rx.Component:
    return rx.el.button(
        question,
        on_click=lambda: ChatState.send_quick_question(question),
        class_name="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full hover:bg-gray-200 transition-colors",
    )


def chat_page() -> rx.Component:
    quick_questions = [
        "Is this property overpriced?",
        "Show me 3BHK options in Pune under 90L",
        "What's the investment potential?",
    ]
    return rx.el.div(
        rx.el.div(
            rx.foreach(ChatState.messages, message_bubble),
            class_name="flex-1 p-4 space-y-4 overflow-y-auto scroll-smooth",
            role="log",
            aria_live="polite",
        ),
        rx.el.div(
            rx.el.div(
                rx.foreach(quick_questions, quick_question_button),
                class_name="flex flex-wrap gap-2 mb-2 px-4",
            ),
            rx.el.form(
                rx.el.input(
                    name="query",
                    placeholder="Ask PropMate AI...",
                    class_name=(
                        "flex-1 px-4 py-2 bg-white border border-gray-300 rounded-l-lg "
                        "focus:outline-none focus:ring-2 focus:ring-teal-500"
                    ),
                ),
                rx.el.button(
                    rx.cond(
                        ChatState.is_processing,
                        rx.spinner(class_name="h-5 w-5", aria_hidden=True),
                        rx.icon("arrow-up", class_name="h-5 w-5"),
                    ),
                    type="submit",
                    class_name=(
                        "px-4 py-2 bg-teal-600 text-white rounded-r-lg hover:bg-teal-700 disabled:bg-gray-400 "
                        "flex items-center justify-center transition-colors duration-200 motion-reduce:transition-none "
                        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500"
                    ),
                    aria_busy=ChatState.is_processing,
                    disabled=ChatState.is_processing,
                ),
                on_submit=ChatState.process_query,
                reset_on_submit=True,
                class_name="flex p-4 bg-gray-100 border-t",
            ),
            class_name="sticky bottom-0",
        ),
        class_name="flex flex-col h-full bg-white",
    )