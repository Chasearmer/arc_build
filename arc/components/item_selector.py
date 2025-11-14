import reflex as rx
from arc.state import CalculatorState
from arc.components.item_card import item_card


def category_button(category: str) -> rx.Component:
    """A button for filtering item categories."""
    is_active = CalculatorState.active_category == category
    return rx.el.button(
        category,
        on_click=lambda: CalculatorState.select_category(category),
        class_name=rx.cond(
            is_active,
            "px-4 py-2 text-sm font-semibold text-white bg-[#22BFFB] rounded-lg shadow-sm",
            "px-4 py-2 text-sm font-semibold text-white bg-[#5D605D] border border-[#5D605D] rounded-lg hover:bg-[#3DEB58]",
        ),
    )


def item_selector() -> rx.Component:
    """Item selector with search, category filters, and item grid."""
    categories = ["All", "Weapon", "Augment", "Shield", "Healing", "Trap"]
    
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.input(
                        id="search-input",
                        placeholder="Search for items... (⌘+K)",
                        on_change=CalculatorState.set_search_query.debounce(300),
                        class_name="w-full pl-10 pr-4 py-2 text-sm bg-[#1a1a1a] text-white border border-[#5D605D] rounded-lg focus:ring-[#22BFFB] focus:border-[#22BFFB] placeholder-gray-500",
                    ),
                    rx.icon(
                        "search",
                        class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500",
                    ),
                    class_name="relative w-full max-w-xs",
                ),
                rx.el.div(
                    rx.foreach(categories, category_button),
                    class_name="flex items-center gap-2",
                ),
                class_name="flex items-center justify-between gap-4",
            ),
            class_name="p-6 pb-4 bg-[#2a2a2a] border-b border-[#5D605D] flex-shrink-0",
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
            class_name="w-full p-6 pt-4 overflow-y-auto flex-1 bg-[#2a2a2a]",
        ),
        class_name="flex flex-col flex-1 bg-[#2a2a2a] overflow-hidden",
    )

