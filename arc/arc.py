import reflex as rx
import reflex_enterprise as rxe
from arc.state import CalculatorState
from arc.components.sidebar import resource_summary_sidebar
from arc.components.loadout_panel import loadout_panel
from arc.components.item_selector import item_selector


def page_header() -> rx.Component:
    """Header at the top of the page with title and navigation links."""
    return rx.el.header(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Arc Raiders Loadout Calculator",
                    class_name="text-2xl font-bold text-white",
                ),
                rx.el.p(
                    "Plan your loadouts and calculate resource requirements",
                    class_name="text-sm text-gray-300 mt-1",
                ),
                class_name="flex-1",
            ),
            rx.el.nav(
                rx.el.a(
                    "Arc Raiders Wiki",
                    href="https://arc-raiders.wiki",
                    target="_blank",
                    class_name="text-sm font-medium text-[#22BFFB] hover:text-[#3DEB58] hover:underline",
                ),
                rx.el.span(
                    "•",
                    class_name="text-gray-500 mx-3",
                ),
                rx.el.a(
                    "Weapon DPS & TTK",
                    href="https://arc-raiders-dps.com",
                    target="_blank",
                    class_name="text-sm font-medium text-[#22BFFB] hover:text-[#3DEB58] hover:underline",
                ),
                class_name="flex items-center",
            ),
            class_name="flex items-center justify-between",
        ),
        class_name="w-full bg-[#1a1a1a] border-b border-[#5D605D] px-8 py-4",
    )


def preset_button(text: str, on_click: rx.event.EventType) -> rx.Component:
    return rx.el.button(
        text,
        on_click=on_click,
        class_name="px-3 py-1.5 text-xs font-semibold text-white bg-[#22BFFB] rounded-md hover:bg-[#3DEB58] transition-colors",
    )


def index() -> rx.Component:
    """The main page of the resource calculator."""
    # Width configuration - adjust these to change the layout ratio
    # Options: w-1/2, w-2/3, w-3/4, w-4/5, etc.
    main_content_width = "w-2/3"  # Loadout + Item Selector
    sidebar_width = "w-1/3"        # Resource Summary
    
    return rxe.dnd.provider(
        rx.el.div(
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
                class_name=f"flex flex-col {main_content_width}",
            ),
            resource_summary_sidebar(width_class=sidebar_width),
            class_name="flex flex-1 bg-[#2a2a2a] font-['Roboto'] overflow-hidden",
        ),
        class_name="flex flex-col h-screen bg-[#2a2a2a] font-['Roboto']",
        ),
    )


app = rxe.App(
    theme=rx.theme(appearance="dark"),
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
