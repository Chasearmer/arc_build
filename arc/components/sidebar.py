import reflex as rx
from arc.state import CalculatorState, ResourceDisplay


def tooltip_wrapper(content: rx.Component, tooltip_text: str) -> rx.Component:
    """Wraps content with a tooltip."""
    return rx.el.div(
        content,
        rx.el.span(
            tooltip_text,
            class_name="invisible group-hover:visible absolute bottom-full left-1/2 -translate-x-1/2 -translate-y-1 px-2 py-1 text-xs font-medium text-gray-800 bg-gray-300 rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-75 delay-700 pointer-events-none z-50",
        ),
        class_name="relative group inline-block",
    )


def resource_card(resource: ResourceDisplay) -> rx.Component:
    """A single resource card with decompose button for refined resources."""
    # Determine colors based on rarity using rx.match for reactive values
    text_color = rx.match(
        resource["rarity"],
        ("Common", "font-semibold text-gray-700"),
        ("Uncommon", "font-semibold text-green-600"),
        ("Rare", "font-semibold text-blue-600"),
        "font-semibold text-purple-600",
    )
    
    icon_color = rx.match(
        resource["rarity"],
        ("Common", "text-gray-700"),
        ("Uncommon", "text-green-600"),
        ("Rare", "text-blue-600"),
        "text-purple-600",
    )
    
    # Check if this resource is decomposed (reactive)
    is_decomposed = CalculatorState.decomposed_resources.contains(resource["id"])
    
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.cond(
                    resource["image"],
                    rx.image(
                        src=resource["image"],
                        width="48px",
                        height="48px",
                        class_name="object-contain",
                    ),
                    rx.icon(
                        "package",
                        size=36,
                        class_name=icon_color,
                    ),
                ),
                rx.el.p(
                    resource["name"],
                    class_name=text_color,
                ),
                class_name="flex items-center gap-3 flex-1",
            ),
            rx.cond(
                resource["resource_type"] == "refined",
                tooltip_wrapper(
                    rx.el.button(
                        rx.icon(
                            "git-branch",
                            size=14,
                        ),
                        on_click=lambda: CalculatorState.toggle_decompose_resource(resource["id"]),
                        class_name="px-2 py-1 text-xs rounded hover:bg-gray-200 transition-colors text-gray-500",
                    ),
                    "Expand",
                ),
                rx.el.span(),
            ),
            rx.el.p(
                resource["quantity"],
                class_name="text-lg font-bold text-gray-800",
            ),
            class_name="flex items-center justify-between gap-2",
        ),
        class_name="p-4 bg-white rounded-lg border border-gray-200",
    )


def decomposed_resource_card(resource: ResourceDisplay) -> rx.Component:
    """A grayed-out card for decomposed resources with a recompose button."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.cond(
                    resource["image"],
                    rx.image(
                        src=resource["image"],
                        width="48px",
                        height="48px",
                        class_name="object-contain opacity-50",
                    ),
                    rx.icon(
                        "package",
                        size=36,
                        class_name="text-gray-400",
                    ),
                ),
                rx.el.p(
                    resource["name"],
                    class_name="font-semibold text-gray-400",
                ),
                class_name="flex items-center gap-3 flex-1",
            ),
            tooltip_wrapper(
                rx.el.button(
                    rx.icon(
                        "rotate-ccw",
                        size=14,
                    ),
                    on_click=lambda: CalculatorState.toggle_decompose_resource(resource["id"]),
                    class_name="px-2 py-1 text-xs rounded hover:bg-gray-200 transition-colors text-gray-500",
                ),
                "Collapse",
            ),
            rx.el.p(
                resource["quantity"],
                class_name="text-lg font-bold text-gray-400",
            ),
            class_name="flex items-center justify-between gap-2",
        ),
        class_name="p-4 bg-gray-50 rounded-lg border border-gray-200",
    )


def resource_summary_sidebar() -> rx.Component:
    """The sidebar component to display the resource summary."""
    return rx.el.aside(
        rx.el.div(
            rx.el.h2(
                "Required Resources", class_name="text-xl font-bold text-gray-800"
            ),
            rx.el.p(
                "Expand refined resources to view crafting materials.", class_name="text-sm text-gray-500 mt-1"
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("trash-2", size=14, class_name="mr-2"),
                    "Clear Loadout",
                    on_click=CalculatorState.clear_selection,
                    class_name="flex-1 flex items-center justify-center px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors",
                ),
                class_name="mt-4 w-full flex gap-2",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("git-branch", size=14, class_name="mr-2"),
                    "Expand All",
                    on_click=CalculatorState.decompose_all_resources,
                    class_name="flex-1 flex items-center justify-center px-3 py-2 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors",
                ),
                rx.el.button(
                    rx.icon("rotate-ccw", size=14, class_name="mr-2"),
                    "Reset",
                    on_click=CalculatorState.reset_decomposition,
                    disabled=~CalculatorState.has_decomposed_resources,
                    class_name=rx.cond(
                        CalculatorState.has_decomposed_resources,
                        "flex-1 flex items-center justify-center px-3 py-2 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors",
                        "flex-1 flex items-center justify-center px-3 py-2 text-xs font-medium text-gray-400 bg-gray-100 border border-gray-200 rounded-lg cursor-not-allowed"
                    ),
                ),
                class_name="mt-2 w-full flex gap-2",
            ),
            class_name="p-6 border-b border-gray-200",
        ),
        rx.el.div(
            rx.cond(
                CalculatorState.has_loadout_items,
                rx.el.div(
                    rx.el.div(
                        rx.foreach(
                            CalculatorState.sorted_total_resources,
                            resource_card,
                        ),
                        class_name="space-y-3",
                    ),
                    rx.cond(
                        CalculatorState.decomposed_resources_display.length() > 0,
                        rx.el.div(
                            rx.el.hr(class_name="border-gray-300 my-6"),
                            rx.el.h3(
                                "Expanded Resources",
                                class_name="text-sm font-bold text-gray-500 uppercase tracking-wide mb-3",
                            ),
                            rx.el.div(
                                rx.foreach(
                                    CalculatorState.decomposed_resources_display,
                                    decomposed_resource_card,
                                ),
                                class_name="space-y-3",
                            ),
                        ),
                        rx.el.span(),
                    ),
                    class_name="p-6",
                ),
                rx.el.div(
                    rx.icon("list-x", size=48, class_name="text-gray-300"),
                    rx.el.p(
                        "No items in loadout", class_name="text-gray-500 font-medium mt-4"
                    ),
                    rx.el.p(
                        "Add items to your loadout to see resource costs.",
                        class_name="text-gray-400 text-sm",
                    ),
                    class_name="flex flex-col items-center justify-center h-full text-center p-6",
                ),
            ),
            class_name="flex-grow overflow-y-auto",
        ),
        class_name="w-1/3 bg-gray-50 border-l border-gray-200 flex-shrink-0 flex flex-col h-screen sticky top-0",
    )