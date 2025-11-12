import reflex as rx
from arc.state import CalculatorState, Item, LoadoutItem


def loadout_tier_selector(slot: str, current_tier: int, index: int | None = None, interactive: bool = True) -> rx.Component:
    """A component to select the tier for a weapon in the loadout."""
    tiers = ["I", "II", "III", "IV"]
    
    if interactive:
        return rx.el.div(
            rx.foreach(
                tiers,
                lambda tier, tier_index: rx.el.button(
                    tier,
                    on_click=lambda: CalculatorState.set_loadout_weapon_tier(
                        slot, tier_index + 1, index
                    ),
                    class_name=rx.cond(
                        current_tier == tier_index + 1,
                        "w-6 h-6 text-xs font-bold text-white bg-sky-500 rounded-md",
                        "w-6 h-6 text-xs font-semibold text-gray-600 bg-gray-200 rounded-md hover:bg-gray-300",
                    ),
                    size="1",
                ),
            ),
            class_name="flex items-center justify-center gap-1",
            on_click=rx.stop_propagation,
        )
    else:
        tier_display = rx.match(
            current_tier,
            (1, "Tier I"),
            (2, "Tier II"),
            (3, "Tier III"),
            (4, "Tier IV"),
            "Tier I",
        )
        return rx.el.div(
            rx.el.span(
                tier_display,
                class_name="text-xs font-semibold text-gray-600",
            ),
            class_name="flex items-center justify-center",
        )


def empty_slot(label: str, slot_size: str = "standard") -> rx.Component:
    """An empty slot placeholder."""
    if slot_size == "augment":
        size_class = "w-32 h-20"
    elif slot_size == "weapon":
        # Width should match 2 augment boxes (w-32 each) + gap between (gap-2 = 0.5rem = 8px)
        # Using w-[264px] which is 2*128px + 8px = 264px
        size_class = "w-[264px] h-40"
    else:  # standard
        size_class = "w-20 h-20"
    
    return rx.el.div(
        rx.el.p(label, class_name="text-xs text-gray-400"),
        class_name=f"{size_class} border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center bg-gray-50",
    )


def item_slot_with_item(item: Item, slot_type: str, index: int | None = None, slot_size: str = "standard", quantity: int = 1, tier: int | None = None) -> rx.Component:
    """Displays an item in a slot with click to remove."""
    if slot_size == "augment":
        size_class = "w-32 h-20"
    elif slot_size == "weapon":
        # Width should match 2 augment boxes (w-32 each) + gap between (gap-2 = 0.5rem = 8px)
        size_class = "w-[264px] h-40"
    else:  # standard
        size_class = "w-20 h-20"
    
    # Map rarity to border color
    border_color = rx.match(
        item["rarity"],
        ("Common", "border-gray-400"),
        ("Uncommon", "border-green-500"),
        ("Rare", "border-blue-500"),
        ("Epic", "border-purple-500"),
        ("Legendary", "border-yellow-500"),
        "border-gray-400",
    )
    
    # For weapon slots (weapon_1, weapon_2), show weapon with tier selector
    if slot_type in ["weapon_1", "weapon_2"]:
        return rx.el.div(
            rx.el.div(
                rx.image(
                    src=item["image"],
                    alt=item["name"],
                    class_name="w-full h-full object-contain",
                ),
                class_name="h-4/5 flex items-center justify-center",
            ),
            rx.el.div(
                rx.cond(
                    tier,
                    loadout_tier_selector(slot_type, tier, index, interactive=True),
                    rx.el.span("Tier I", class_name="text-xs font-semibold text-gray-600"),
                ),
                on_click=rx.stop_propagation,
                class_name="h-1/5 flex items-center justify-center px-1",
            ),
            on_click=lambda: CalculatorState.unequip_from_loadout(slot_type, index),
            class_name=f"{size_class} border-2 {border_color} rounded-lg overflow-hidden cursor-pointer hover:opacity-80 transition-opacity bg-white flex flex-col",
        )
    
    # For backpack slots, check if it's a weapon to show tier display, otherwise show quantity controls
    elif slot_type == "backpack":
        return rx.cond(
            item["category"] == "Weapon",
            # Weapon in backpack - show tier display (non-interactive)
            rx.el.div(
                rx.el.div(
                    rx.image(
                        src=item["image"],
                        alt=item["name"],
                        class_name="w-full h-full object-contain",
                    ),
                    class_name="h-4/5 flex items-center justify-center",
                ),
                rx.el.div(
                    rx.cond(
                        tier,
                        loadout_tier_selector(slot_type, tier, index, interactive=False),
                        rx.el.span("Tier I", class_name="text-xs font-semibold text-gray-600"),
                    ),
                    on_click=rx.stop_propagation,
                    class_name="h-1/5 flex items-center justify-center px-1",
                ),
                on_click=lambda: CalculatorState.unequip_from_loadout(slot_type, index),
                class_name=f"{size_class} border-2 {border_color} rounded-lg overflow-hidden cursor-pointer hover:opacity-80 transition-opacity bg-white flex flex-col",
            ),
            # Non-weapon in backpack - show quantity controls
            rx.el.div(
                rx.el.div(
                    rx.image(
                        src=item["image"],
                        alt=item["name"],
                        class_name="w-full h-full object-contain",
                    ),
                    class_name="h-4/5 flex items-center justify-center",
                ),
                rx.el.div(
                    rx.el.button(
                        "-",
                        on_click=lambda: CalculatorState.decrease_item_quantity(slot_type, index),
                        class_name="w-4 h-4 text-xs font-bold text-gray-700 bg-gray-200 rounded hover:bg-gray-300 flex items-center justify-center",
                    ),
                    rx.el.span(
                        f"x{quantity}",
                        class_name="text-xs font-semibold text-gray-700",
                    ),
                    rx.el.button(
                        "+",
                        on_click=lambda: CalculatorState.increase_item_quantity(slot_type, index),
                        class_name="w-4 h-4 text-xs font-bold text-gray-700 bg-gray-200 rounded hover:bg-gray-300 flex items-center justify-center",
                    ),
                    on_click=rx.stop_propagation,
                    class_name="h-1/5 flex items-center justify-between gap-1 px-1",
                ),
                on_click=lambda: CalculatorState.unequip_from_loadout(slot_type, index),
                class_name=f"{size_class} border-2 {border_color} rounded-lg overflow-hidden cursor-pointer hover:opacity-80 transition-opacity bg-white flex flex-col",
            ),
        )
    
    # For quick_use and safe_pocket slots, show quantity controls
    elif slot_type in ["quick_use", "safe_pocket"]:
        return rx.el.div(
            rx.el.div(
                rx.image(
                    src=item["image"],
                    alt=item["name"],
                    class_name="w-full h-full object-contain",
                ),
                class_name="h-4/5 flex items-center justify-center",
            ),
            rx.el.div(
                rx.el.button(
                    "-",
                    on_click=lambda: CalculatorState.decrease_item_quantity(slot_type, index),
                    class_name="w-4 h-4 text-xs font-bold text-gray-700 bg-gray-200 rounded hover:bg-gray-300 flex items-center justify-center",
                ),
                rx.el.span(
                    f"x{quantity}",
                    class_name="text-xs font-semibold text-gray-700",
                ),
                rx.el.button(
                    "+",
                    on_click=lambda: CalculatorState.increase_item_quantity(slot_type, index),
                    class_name="w-4 h-4 text-xs font-bold text-gray-700 bg-gray-200 rounded hover:bg-gray-300 flex items-center justify-center",
                ),
                on_click=rx.stop_propagation,
                class_name="h-1/5 flex items-center justify-between gap-1 px-1",
            ),
            on_click=lambda: CalculatorState.unequip_from_loadout(slot_type, index),
            class_name=f"{size_class} border-2 {border_color} rounded-lg overflow-hidden cursor-pointer hover:opacity-80 transition-opacity bg-white flex flex-col",
        )
    
    # For other equipment slots (augment, shield)
    else:
        return rx.el.div(
            rx.image(
                src=item["image"],
                alt=item["name"],
                class_name="w-full h-full object-contain",
            ),
            on_click=lambda: CalculatorState.unequip_from_loadout(slot_type, index),
            class_name=f"{size_class} border-2 {border_color} rounded-lg overflow-hidden cursor-pointer hover:opacity-80 transition-opacity bg-white",
        )


def equipment_section() -> rx.Component:
    """The Equipment section with augment, shield, and weapon slots."""
    return rx.el.div(
        rx.el.h3(
            "EQUIPMENT",
            class_name="text-sm font-bold text-gray-700 mb-3 tracking-wide",
        ),
        rx.el.div(
            rx.cond(
                CalculatorState.loadout_augment_item,
                item_slot_with_item(CalculatorState.loadout_augment_item, "augment", slot_size="augment"),
                empty_slot("Augment", slot_size="augment"),
            ),
            rx.cond(
                CalculatorState.loadout_shield_item,
                item_slot_with_item(CalculatorState.loadout_shield_item, "shield", slot_size="augment"),
                empty_slot("Shield", slot_size="augment"),
            ),
            class_name="flex gap-2 mb-2",
        ),
        rx.cond(
            CalculatorState.loadout_weapon_1_item,
            item_slot_with_item(
                CalculatorState.loadout_weapon_1_item,
                "weapon_1",
                slot_size="weapon",
                tier=rx.cond(
                    CalculatorState.loadout_weapon_1,
                    CalculatorState.loadout_weapon_1.get("tier", 1),
                    1
                )
            ),
            empty_slot("Weapon 1", slot_size="weapon"),
        ),
        rx.cond(
            CalculatorState.loadout_weapon_2_item,
            item_slot_with_item(
                CalculatorState.loadout_weapon_2_item,
                "weapon_2",
                slot_size="weapon",
                tier=rx.cond(
                    CalculatorState.loadout_weapon_2,
                    CalculatorState.loadout_weapon_2.get("tier", 1),
                    1
                )
            ),
            empty_slot("Weapon 2", slot_size="weapon"),
        ),
        class_name="flex flex-col gap-2 flex-[3]",
    )


def backpack_section() -> rx.Component:
    """The Backpack section with a grid of slots."""
    all_slots = rx.Var.range(CalculatorState.max_backpack_slots)
    
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "BACKPACK",
                class_name="text-sm font-bold text-gray-700 tracking-wide",
            ),
            rx.el.p(
                f"{CalculatorState.loadout_backpack.length()}/{CalculatorState.max_backpack_slots}",
                class_name="text-xs text-gray-500",
            ),
            class_name="flex items-center gap-2 mb-3",
        ),
        rx.el.div(
            rx.el.div(
                rx.foreach(
                    all_slots,
                    lambda i: rx.cond(
                        i < CalculatorState.loadout_backpack.length(),
                        item_slot_with_item(
                            CalculatorState.loadout_backpack_items[i],
                            "backpack",
                            i,
                            quantity=CalculatorState.loadout_backpack[i]["quantity"],
                            tier=CalculatorState.loadout_backpack[i].get("tier")
                        ),
                        empty_slot(""),
                    ),
                ),
                class_name="grid grid-cols-4 gap-2 w-fit",
            ),
        ),
        class_name="flex-[4] flex flex-col",
    )


def quick_use_section() -> rx.Component:
    """The Quick Use section."""
    all_slots = rx.Var.range(CalculatorState.max_quick_use_slots)
    
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "QUICK USE",
                class_name="text-sm font-bold text-gray-700 tracking-wide",
            ),
            rx.el.p(
                f"{CalculatorState.loadout_quick_use.length()}/{CalculatorState.max_quick_use_slots}",
                class_name="text-xs text-gray-500",
            ),
            class_name="flex items-center gap-2 mb-3",
        ),
        rx.el.div(
            rx.el.div(
                rx.foreach(
                    all_slots,
                    lambda i: rx.cond(
                        i < CalculatorState.loadout_quick_use.length(),
                        item_slot_with_item(
                            CalculatorState.loadout_quick_use_items[i],
                            "quick_use",
                            i,
                            quantity=CalculatorState.loadout_quick_use[i]["quantity"]
                        ),
                        empty_slot(""),
                    ),
                ),
                class_name="grid grid-cols-3 gap-2 w-fit",
            ),
        ),
    )


def safe_pocket_section() -> rx.Component:
    """The Safe Pocket section."""
    all_slots = rx.Var.range(CalculatorState.max_safe_pocket_slots)
    
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "SAFE POCKET",
                class_name="text-sm font-bold text-gray-700 tracking-wide",
            ),
            rx.el.p(
                f"{CalculatorState.loadout_safe_pocket.length()}/{CalculatorState.max_safe_pocket_slots}",
                class_name="text-xs text-gray-500",
            ),
            class_name="flex items-center gap-2 mb-3",
        ),
        rx.cond(
            CalculatorState.max_safe_pocket_slots > 0,
            rx.el.div(
                rx.el.div(
                    rx.foreach(
                        all_slots,
                        lambda i: rx.cond(
                            i < CalculatorState.loadout_safe_pocket.length(),
                            item_slot_with_item(
                                CalculatorState.loadout_safe_pocket_items[i],
                                "safe_pocket",
                                i,
                                quantity=CalculatorState.loadout_safe_pocket[i]["quantity"]
                            ),
                            empty_slot(""),
                        ),
                    ),
                    class_name="grid grid-cols-1 gap-2 w-fit",
                ),
            ),
            rx.el.div(
                rx.icon("lock", size=32, class_name="text-gray-300"),
                rx.el.p(
                    "No safe pocket",
                    class_name="text-xs text-gray-400 mt-2",
                ),
                class_name="flex flex-col items-center justify-center py-8",
            ),
        ),
        class_name="mt-auto",
    )


def loadout_panel() -> rx.Component:
    """The main loadout panel component."""
    return rx.el.div(
        equipment_section(),
        backpack_section(),
        rx.el.div(
            quick_use_section(),
            safe_pocket_section(),
            class_name="flex flex-col gap-4 flex-[3]",
        ),
        class_name="flex gap-4 px-4 py-6 w-full bg-white border-b border-gray-200 flex-1 overflow-y-auto",
    )

