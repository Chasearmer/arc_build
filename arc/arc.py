import reflex as rx
from arc.state import CalculatorState
from arc.components.sidebar import resource_summary_sidebar
from arc.components.loadout_panel import loadout_panel
from arc.components.dnd_demo import dnd_demo_panel
from arc.components.item_selector import item_selector


def page_header() -> rx.Component:
    """Header at the top of the page with title and navigation links."""
    return rx.el.header(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Arc Raiders Loadout Calculator",
                    class_name="text-2xl font-bold text-gray-900",
                ),
                rx.el.p(
                    "Plan your loadouts and calculate resource requirements",
                    class_name="text-sm text-gray-600 mt-1",
                ),
                class_name="flex-1",
            ),
            rx.el.nav(
                rx.el.a(
                    "Arc Raiders Wiki",
                    href="https://arc-raiders.wiki",
                    target="_blank",
                    class_name="text-sm font-medium text-sky-600 hover:text-sky-700 hover:underline",
                ),
                rx.el.span(
                    "•",
                    class_name="text-gray-400 mx-3",
                ),
                rx.el.a(
                    "Weapon DPS & TTK",
                    href="https://arc-raiders-dps.com",
                    target="_blank",
                    class_name="text-sm font-medium text-sky-600 hover:text-sky-700 hover:underline",
                ),
                class_name="flex items-center",
            ),
            class_name="flex items-center justify-between",
        ),
        class_name="w-full bg-white border-b border-gray-200 px-8 py-4",
    )


def preset_button(text: str, on_click: rx.event.EventType) -> rx.Component:
    return rx.el.button(
        text,
        on_click=on_click,
        class_name="px-3 py-1.5 text-xs font-semibold text-sky-700 bg-sky-100 rounded-md hover:bg-sky-200 transition-colors",
    )


def index() -> rx.Component:
    """The main page of the resource calculator."""
    return rx.el.div(
        rx.window_event_listener(
            on_key_down=lambda event: rx.call_script(
                "(e) => { if (e.key === 'k' && (e.metaKey || e.ctrlKey)) { e.preventDefault(); return 'focus_search'; } if (e.key === 'Escape') { return 'handle_escape'; } return null; }",
                callback=CalculatorState.handle_key_event,
            )
        ),
        page_header(),
        rx.el.main(
            rx.el.div(
                loadout_panel(),
                item_selector(),
                class_name="flex flex-col w-1/2",
            ),
            resource_summary_sidebar(),
            rx.el.aside(
                dnd_demo_panel(),
                class_name="w-1/4 bg-gray-50 border-l border-gray-200 flex-shrink-0 flex flex-col h-screen sticky top-0 overflow-hidden",
            ),
            class_name="flex flex-1 bg-white font-['Roboto'] overflow-hidden",
        ),
        class_name="flex flex-col h-screen bg-white font-['Roboto']",
    )


import reflex_enterprise as rxe

app = rxe.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index)
