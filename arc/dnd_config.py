"""Drag-and-drop configuration constants for the loadout system."""

from typing import Literal

SlotType = Literal["augment", "shield", "weapon", "backpack", "quick_use", "safe_pocket"]

DRAG_TYPES = {
    "Weapon": "ITEM_WEAPON",
    "Augment": "ITEM_AUGMENT",
    "Shield": "ITEM_SHIELD",
    "Healing": "ITEM_HEALING",
    "Trap": "ITEM_TRAP",
    "Gear": "ITEM_GEAR",
    "Gadget": "ITEM_GADGET",
    "Tool": "ITEM_TOOL",
}

SLOT_ACCEPTANCE_RULES: dict[str, list[str]] = {
    "augment": ["ITEM_AUGMENT"],
    "shield": ["ITEM_SHIELD"],
    "weapon": ["ITEM_WEAPON"],
    "backpack": ["ITEM_WEAPON", "ITEM_HEALING", "ITEM_TRAP", "ITEM_GEAR", "ITEM_GADGET", "ITEM_TOOL", "ITEM_AUGMENT", "ITEM_SHIELD"],
    "quick_use": ["ITEM_HEALING", "ITEM_TRAP"],
    "safe_pocket": ["ITEM_HEALING", "ITEM_TRAP", "ITEM_GEAR", "ITEM_GADGET", "ITEM_TOOL", "ITEM_AUGMENT", "ITEM_SHIELD"],
}

