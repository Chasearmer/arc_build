import reflex as rx
from arc.state import Item, CalculatorState
from arc.components.tier_selector import tier_selector


def item_card(item: Item, key: str | int | None = None) -> rx.Component:
    """A compact card that displays just the item image with hover popup.
    
    This is a click-only card (not draggable). Items in the loadout panel are draggable.
    """
    rarity_color = CalculatorState.rarity_colors.get(item["rarity"], "text-gray-500")
    selected_tier = CalculatorState.selected_weapon_tiers.get(item["id"], 1)
    
    # Map rarity to full border class names
    card_class = rx.match(
        item["rarity"],
        ("Common", "group p-3 rounded-xl border-2 border-[#5D605D] bg-[#1a1a1a] shadow-sm cursor-pointer transition-all hover:shadow-lg hover:-translate-y-1 flex flex-col h-40"),
        ("Uncommon", "group p-3 rounded-xl border-2 border-[#3DEB58] bg-[#1a1a1a] shadow-sm cursor-pointer transition-all hover:shadow-lg hover:-translate-y-1 flex flex-col h-40"),
        ("Rare", "group p-3 rounded-xl border-2 border-[#22BFFB] bg-[#1a1a1a] shadow-sm cursor-pointer transition-all hover:shadow-lg hover:-translate-y-1 flex flex-col h-40"),
        ("Epic", "group p-3 rounded-xl border-2 border-[#CB008A] bg-[#1a1a1a] shadow-sm cursor-pointer transition-all hover:shadow-lg hover:-translate-y-1 flex flex-col h-40"),
        ("Legendary", "group p-3 rounded-xl border-2 border-[#F9BC0A] bg-[#1a1a1a] shadow-sm cursor-pointer transition-all hover:shadow-lg hover:-translate-y-1 flex flex-col h-40"),
        "group p-3 rounded-xl border-2 border-[#5D605D] bg-[#1a1a1a] shadow-sm cursor-pointer transition-all hover:shadow-lg hover:-translate-y-1 flex flex-col h-40",
    )

    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.cond(
                    item["image"],
                    rx.image(
                        src=item["image"],
                        alt=item["name"],
                        class_name="w-full h-full object-contain",
                    ),
                    rx.icon(item["icon"], size=48, class_name="text-[#22BFFB]"),
                ),
                class_name="flex items-center justify-center h-4/5",
            ),
            rx.el.div(
                rx.cond(
                    item["category"] == "Weapon",
                    tier_selector(item["id"]),
                    rx.fragment(),
                ),
                class_name="flex items-center h-1/5",
            ),
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        item["name"],
                        class_name="font-semibold text-base text-white mb-1",
                    ),
                    rx.el.p(
                        item["rarity"],
                        class_name=f"text-sm font-medium {rarity_color} mb-2",
                    ),
                    rx.el.p(
                        item["category"],
                        class_name="text-xs text-gray-400 mb-3",
                    ),
                    # Show resources for non-weapon items only
                    rx.cond(
                        item["resources"].length() > 0,
                        rx.el.div(
                            rx.el.p(
                                "Resources:",
                                class_name="text-xs font-semibold text-white mb-2",
                            ),
                            rx.el.div(
                                rx.foreach(
                                    item["resources"],
                                    lambda resource: rx.el.div(
                                        rx.el.p(
                                            resource["quantity"],
                                            class_name="font-semibold text-xs text-white",
                                        ),
                                        rx.el.p(
                                            CalculatorState.get_resource_name(resource["resource"]),
                                            class_name="text-xs text-gray-300",
                                        ),
                                        class_name="flex items-center gap-1.5 bg-[#5D605D] px-2 py-1 rounded-md",
                                    ),
                                ),
                                class_name="flex flex-wrap gap-1.5",
                            ),
                        ),
                        rx.fragment(),
                    ),
                    # For weapons, show a note about tier-based resources
                    rx.cond(
                        item["category"] == "Weapon",
                        rx.el.p(
                            f"Resources vary by tier (currently Tier {selected_tier})",
                            class_name="text-xs text-gray-400 italic",
                        ),
                        rx.fragment(),
                    ),
                    class_name="p-3",
                ),
            ),
            class_name="absolute left-full top-0 ml-2 w-64 bg-[#1a1a1a] border-2 border-[#5D605D] rounded-lg shadow-xl invisible group-hover:visible opacity-0 group-hover:opacity-100 transition-all duration-200 delay-500 group-hover:delay-500 pointer-events-none",
            style={"z-index": "9999"},
        ),
        on_click=lambda: CalculatorState.auto_equip_item(item["id"]),
        class_name=card_class,
    )