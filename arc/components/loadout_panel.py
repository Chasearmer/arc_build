import reflex as rx
import reflex_enterprise as rxe
from arc.state import CalculatorState, Item, LoadoutItem
from arc.dnd_config import DRAG_TYPES, SLOT_ACCEPTANCE_RULES


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


def draggable_loadout_item(item: Item, slot_type: str, position: int, index: int | None = None, slot_size: str = "standard", quantity: int = 1, tier: int | None = None) -> rx.Component:
    """A draggable item that's already in the loadout."""
    drag_params = rxe.dnd.Draggable.collected_params
    
    if slot_size == "augment":
        size_class = "w-32 h-20"
    elif slot_size == "weapon":
        size_class = "w-[264px] h-40"
    else:  # standard
        size_class = "w-20 h-20"
    
    border_color_solid = rx.match(
        item["rarity"],
        ("Common", "gray.400"),
        ("Uncommon", "green.500"),
        ("Rare", "blue.500"),
        ("Epic", "purple.500"),
        ("Legendary", "yellow.500"),
        "gray.400",
    )
    
    border_color = rx.match(
        item["rarity"],
        ("Common", "border-gray-400"),
        ("Uncommon", "border-green-500"),
        ("Rare", "border-blue-500"),
        ("Epic", "border-purple-500"),
        ("Legendary", "border-yellow-500"),
        "border-gray-400",
    )
    
    item_content = item_slot_with_item_content(item, slot_type, index, slot_size, quantity, tier, border_color)
    
    # Use rx.match to dynamically determine drag type based on item category
    drag_type = rx.match(
        item["category"],
        ("Weapon", "ITEM_WEAPON"),
        ("Augment", "ITEM_AUGMENT"),
        ("Shield", "ITEM_SHIELD"),
        ("Healing", "ITEM_HEALING"),
        ("Trap", "ITEM_TRAP"),
        ("Gear", "ITEM_GEAR"),
        ("Gadget", "ITEM_GADGET"),
        ("Tool", "ITEM_TOOL"),
        "ITEM_GEAR",  # default
    )
    
    return rxe.dnd.draggable(
        item_content,
        type=drag_type,
        item={
            "item_id": item["id"],
            "category": item["category"],
            "source": "loadout",
            "source_slot_type": slot_type,
            "source_position": position,
            "tier": tier,
            "quantity": quantity,
        },
    )


def item_slot_with_item_content(item: Item, slot_type: str, index: int | None = None, slot_size: str = "standard", quantity: int = 1, tier: int | None = None, border_color: str = "border-gray-400") -> rx.Component:
    """Displays an item in a slot with click to remove (content only, no drag wrapper)."""
    if slot_size == "augment":
        size_class = "w-32 h-20"
    elif slot_size == "weapon":
        size_class = "w-[264px] h-40"
    else:  # standard
        size_class = "w-20 h-20"
    
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


def drop_target_augment() -> rx.Component:
    """Drop target for the augment slot."""
    drop_params = rxe.dnd.DropTarget.collected_params
    
    return rxe.dnd.drop_target(
        rx.cond(
            CalculatorState.loadout_augment_item,
            draggable_loadout_item(
                CalculatorState.loadout_augment_item,
                "augment",
                0,
                slot_size="augment"
            ),
            empty_slot("Augment", slot_size="augment"),
        ),
        accept=SLOT_ACCEPTANCE_RULES["augment"],
        on_drop=lambda item: CalculatorState.handle_drop_to_slot("augment", 0, item),
        border="2px solid",
        border_color=rx.cond(
            drop_params.is_over & drop_params.can_drop,
            "green.500",
            rx.cond(drop_params.is_over, "red.500", "transparent")
        ),
        bg=rx.cond(
            drop_params.is_over & drop_params.can_drop,
            "green.50",
            rx.cond(drop_params.is_over, "red.50", "transparent")
        ),
        border_radius="8px",
        width="fit-content",
    )


def drop_target_shield() -> rx.Component:
    """Drop target for the shield slot."""
    drop_params = rxe.dnd.DropTarget.collected_params
    
    return rxe.dnd.drop_target(
        rx.cond(
            CalculatorState.loadout_shield_item,
            draggable_loadout_item(
                CalculatorState.loadout_shield_item,
                "shield",
                0,
                slot_size="augment"
            ),
            empty_slot("Shield", slot_size="augment"),
        ),
        accept=SLOT_ACCEPTANCE_RULES["shield"],
        on_drop=lambda item: CalculatorState.handle_drop_to_slot("shield", 0, item),
        border="2px solid",
        border_color=rx.cond(
            drop_params.is_over & drop_params.can_drop,
            "green.500",
            rx.cond(drop_params.is_over, "red.500", "transparent")
        ),
        bg=rx.cond(
            drop_params.is_over & drop_params.can_drop,
            "green.50",
            rx.cond(drop_params.is_over, "red.50", "transparent")
        ),
        border_radius="8px",
        width="fit-content",
    )


def drop_target_weapon(position: int) -> rx.Component:
    """Drop target for weapon slot 1 or 2."""
    drop_params = rxe.dnd.DropTarget.collected_params
    weapon_slot = f"weapon_{position + 1}"
    weapon_data = CalculatorState.loadout_weapon_1 if position == 0 else CalculatorState.loadout_weapon_2
    weapon_item = CalculatorState.loadout_weapon_1_item if position == 0 else CalculatorState.loadout_weapon_2_item
    
    return rxe.dnd.drop_target(
        rx.cond(
            weapon_item,
            draggable_loadout_item(
                weapon_item,
                weapon_slot,
                position,
                slot_size="weapon",
                tier=rx.cond(weapon_data, weapon_data.get("tier", 1), 1)
            ),
            empty_slot(f"Weapon {position + 1}", slot_size="weapon"),
        ),
        accept=SLOT_ACCEPTANCE_RULES["weapon"],
        on_drop=lambda item: CalculatorState.handle_drop_to_slot("weapon", position, item),
        border="2px solid",
        border_color=rx.cond(
            drop_params.is_over & drop_params.can_drop,
            "green.500",
            rx.cond(drop_params.is_over, "red.500", "transparent")
        ),
        bg=rx.cond(
            drop_params.is_over & drop_params.can_drop,
            "green.50",
            rx.cond(drop_params.is_over, "red.50", "transparent")
        ),
        border_radius="8px",
        width="fit-content",
    )


def equipment_section() -> rx.Component:
    """The Equipment section with augment, shield, and weapon slots."""
    return rx.el.div(
        rx.el.h3(
            "EQUIPMENT",
            class_name="text-sm font-bold text-gray-700 mb-3 tracking-wide",
        ),
        rx.el.div(
            drop_target_augment(),
            drop_target_shield(),
            class_name="flex gap-2 mb-2",
        ),
        drop_target_weapon(0),
        drop_target_weapon(1),
        class_name="flex flex-col gap-2 flex-[3]",
    )


def drop_target_backpack_slot(position: int) -> rx.Component:
    """Drop target for a specific backpack slot position."""
    drop_params = rxe.dnd.DropTarget.collected_params
    
    # Check if slot has an actual item (not just a None placeholder)
    has_item = (position < CalculatorState.loadout_backpack.length()) & (
        CalculatorState.loadout_backpack[position]["item_id"] != None
    )
    
    return rxe.dnd.drop_target(
        rx.cond(
            has_item,
            draggable_loadout_item(
                CalculatorState.loadout_backpack_items[position],
                "backpack",
                position,
                index=position,
                quantity=CalculatorState.loadout_backpack[position]["quantity"],
                tier=CalculatorState.loadout_backpack[position].get("tier")
            ),
            empty_slot(""),
        ),
        accept=SLOT_ACCEPTANCE_RULES["backpack"],
        on_drop=lambda item: CalculatorState.handle_drop_to_slot("backpack", position, item),
        border="2px solid",
        border_color=rx.cond(
            drop_params.is_over & drop_params.can_drop,
            "green.500",
            rx.cond(drop_params.is_over, "red.500", "transparent")
        ),
        bg=rx.cond(
            drop_params.is_over & drop_params.can_drop,
            "green.50",
            rx.cond(drop_params.is_over, "red.50", "transparent")
        ),
        border_radius="8px",
        width="fit-content",
    )


def backpack_section() -> rx.Component:
    """The Backpack section with a grid of slots."""
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
            rx.grid(
                drop_target_backpack_slot(0),
                rx.cond(CalculatorState.max_backpack_slots >= 2, drop_target_backpack_slot(1)),
                rx.cond(CalculatorState.max_backpack_slots >= 3, drop_target_backpack_slot(2)),
                rx.cond(CalculatorState.max_backpack_slots >= 4, drop_target_backpack_slot(3)),
                rx.cond(CalculatorState.max_backpack_slots >= 5, drop_target_backpack_slot(4)),
                rx.cond(CalculatorState.max_backpack_slots >= 6, drop_target_backpack_slot(5)),
                rx.cond(CalculatorState.max_backpack_slots >= 7, drop_target_backpack_slot(6)),
                rx.cond(CalculatorState.max_backpack_slots >= 8, drop_target_backpack_slot(7)),
                rx.cond(CalculatorState.max_backpack_slots >= 9, drop_target_backpack_slot(8)),
                rx.cond(CalculatorState.max_backpack_slots >= 10, drop_target_backpack_slot(9)),
                rx.cond(CalculatorState.max_backpack_slots >= 11, drop_target_backpack_slot(10)),
                rx.cond(CalculatorState.max_backpack_slots >= 12, drop_target_backpack_slot(11)),
                rx.cond(CalculatorState.max_backpack_slots >= 13, drop_target_backpack_slot(12)),
                rx.cond(CalculatorState.max_backpack_slots >= 14, drop_target_backpack_slot(13)),
                columns="4",
                spacing="2",
            ),
        ),
        class_name="flex-[4] flex flex-col",
    )


def drop_target_quick_use_slot(position: int) -> rx.Component:
    """Drop target for a specific quick use slot position."""
    drop_params = rxe.dnd.DropTarget.collected_params
    
    # Check if slot has an actual item (not just a None placeholder)
    has_item = (position < CalculatorState.loadout_quick_use.length()) & (
        CalculatorState.loadout_quick_use[position]["item_id"] != None
    )
    
    return rxe.dnd.drop_target(
        rx.cond(
            has_item,
            draggable_loadout_item(
                CalculatorState.loadout_quick_use_items[position],
                "quick_use",
                position,
                index=position,
                quantity=CalculatorState.loadout_quick_use[position]["quantity"]
            ),
            empty_slot(""),
        ),
        accept=SLOT_ACCEPTANCE_RULES["quick_use"],
        on_drop=lambda item: CalculatorState.handle_drop_to_slot("quick_use", position, item),
        border="2px solid",
        border_color=rx.cond(
            drop_params.is_over & drop_params.can_drop,
            "green.500",
            rx.cond(drop_params.is_over, "red.500", "transparent")
        ),
        bg=rx.cond(
            drop_params.is_over & drop_params.can_drop,
            "green.50",
            rx.cond(drop_params.is_over, "red.50", "transparent")
        ),
        border_radius="8px",
        width="fit-content",
    )


def quick_use_section() -> rx.Component:
    """The Quick Use section."""
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
        rx.grid(
            drop_target_quick_use_slot(0),
            rx.cond(CalculatorState.max_quick_use_slots >= 2, drop_target_quick_use_slot(1)),
            rx.cond(CalculatorState.max_quick_use_slots >= 3, drop_target_quick_use_slot(2)),
            rx.cond(CalculatorState.max_quick_use_slots >= 4, drop_target_quick_use_slot(3)),
            columns="3",
            spacing="2",
        ),
    )


def drop_target_safe_pocket_slot(position: int) -> rx.Component:
    """Drop target for a specific safe pocket slot position."""
    drop_params = rxe.dnd.DropTarget.collected_params
    
    # Check if slot has an actual item (not just a None placeholder)
    has_item = (position < CalculatorState.loadout_safe_pocket.length()) & (
        CalculatorState.loadout_safe_pocket[position]["item_id"] != None
    )
    
    return rxe.dnd.drop_target(
        rx.cond(
            has_item,
            draggable_loadout_item(
                CalculatorState.loadout_safe_pocket_items[position],
                "safe_pocket",
                position,
                index=position,
                quantity=CalculatorState.loadout_safe_pocket[position]["quantity"]
            ),
            empty_slot(""),
        ),
        accept=SLOT_ACCEPTANCE_RULES["safe_pocket"],
        on_drop=lambda item: CalculatorState.handle_drop_to_slot("safe_pocket", position, item),
        border="2px solid",
        border_color=rx.cond(
            drop_params.is_over & drop_params.can_drop,
            "green.500",
            rx.cond(drop_params.is_over, "red.500", "transparent")
        ),
        bg=rx.cond(
            drop_params.is_over & drop_params.can_drop,
            "green.50",
            rx.cond(drop_params.is_over, "red.50", "transparent")
        ),
        border_radius="8px",
        width="fit-content",
    )


def safe_pocket_section() -> rx.Component:
    """The Safe Pocket section."""
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
                rx.grid(
                    drop_target_safe_pocket_slot(0),
                    rx.cond(CalculatorState.max_safe_pocket_slots >= 2, drop_target_safe_pocket_slot(1)),
                    columns="1",
                    spacing="2",
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

