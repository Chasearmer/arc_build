import reflex as rx
from arc.state import CalculatorState
from arc.components.item_card import item_card
from arc.components.sidebar import resource_summary_sidebar
from arc.components.loadout_panel import loadout_panel


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


def category_button(category: str) -> rx.Component:
    """A button for filtering item categories."""
    is_active = CalculatorState.active_category == category
    return rx.el.button(
        category,
        on_click=lambda: CalculatorState.select_category(category),
        class_name=rx.cond(
            is_active,
            "px-4 py-2 text-sm font-semibold text-white bg-sky-500 rounded-lg shadow-sm",
            "px-4 py-2 text-sm font-semibold text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50",
        ),
    )


def preset_button(text: str, on_click: rx.event.EventType) -> rx.Component:
    return rx.el.button(
        text,
        on_click=on_click,
        class_name="px-3 py-1.5 text-xs font-semibold text-sky-700 bg-sky-100 rounded-md hover:bg-sky-200 transition-colors",
    )


def index() -> rx.Component:
    """The main page of the resource calculator."""
    categories = ["All", "Weapon", "Augment", "Shield", "Healing", "Trap"]
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
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.el.input(
                                    id="search-input",
                                    placeholder="Search for items... (⌘+K)",
                                    on_change=CalculatorState.set_search_query.debounce(
                                        300
                                    ),
                                    class_name="w-full pl-10 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:ring-sky-500 focus:border-sky-500",
                                ),
                                rx.icon(
                                    "search",
                                    class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400",
                                ),
                                class_name="relative w-full max-w-xs",
                            ),
                            rx.el.div(
                                rx.foreach(categories, category_button),
                                class_name="flex items-center gap-2",
                            ),
                            class_name="flex items-center justify-between gap-4",
                        ),
                        class_name="p-6 pb-4 bg-white border-b border-gray-200 flex-shrink-0",
                    ),
                    rx.el.div(
                        rx.grid(
                            rx.foreach(
                                CalculatorState.filtered_items,
                                lambda item: item_card(item, key=item["id"]),
                            ),
                            columns="1",
                            gap="4",
                            width="100%",
                            class_name="grid-cols-6 gap-x-4 gap-y-4",
                        ),
                        class_name="w-full p-6 pt-4 overflow-y-auto flex-1",
                    ),
                    class_name="flex flex-col flex-1 bg-white overflow-hidden",
                ),
                class_name="flex flex-col w-2/3",
            ),
            resource_summary_sidebar(),
            class_name="flex flex-1 bg-white font-['Roboto'] overflow-hidden",
        ),
        class_name="flex flex-col h-screen bg-white font-['Roboto']",
    )


app = rx.App(
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
