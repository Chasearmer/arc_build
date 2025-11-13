# Drag-and-Drop Implementation Summary

## Overview

This document details the implementation of drag-and-drop functionality for the Arc Raiders Loadout Calculator, including architectural decisions, code structure, challenges encountered, and lessons learned.

## Implementation Architecture

### Design Decision: Hybrid Approach

After encountering technical limitations with Reflex Enterprise DnD, we implemented a **hybrid approach**:

- **Item Selector (Sidebar)**: Click-only functionality
- **Loadout Panel**: Full drag-and-drop support between all slots

This architecture provides:
- ✅ Intuitive click-to-add from sidebar
- ✅ Flexible drag-to-rearrange within loadout
- ✅ No TypedDict/rx.foreach compatibility issues
- ✅ Clean, maintainable codebase

### Core Components

1. **DnD Configuration** (`arc/dnd_config.py`)
2. **State Management** (`arc/state.py`)
3. **Loadout Panel UI** (`arc/components/loadout_panel.py`)
4. **Item Cards** (`arc/components/item_card.py`)
5. **Main App Wrapper** (`arc/arc.py`)

---

## 1. DnD Configuration (`arc/dnd_config.py`)

Centralized configuration for drag types and slot acceptance rules.

```python
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
    "backpack": ["ITEM_WEAPON", "ITEM_HEALING", "ITEM_TRAP", "ITEM_GEAR", 
                 "ITEM_GADGET", "ITEM_TOOL", "ITEM_AUGMENT", "ITEM_SHIELD"],
    "quick_use": ["ITEM_HEALING", "ITEM_TRAP"],
    "safe_pocket": ["ITEM_HEALING", "ITEM_TRAP", "ITEM_GEAR", "ITEM_GADGET", 
                    "ITEM_TOOL", "ITEM_AUGMENT", "ITEM_SHIELD"],
}
```

**Key Design Choices:**
- **Backpack accepts everything**: Maximum flexibility for item storage
- **Safe Pocket accepts everything except weapons**: Balances game logic with usability
- **Type-safe Literal**: Compile-time validation of slot types

---

## 2. State Management (`arc/state.py`)

### Event Handler: `handle_drop_to_slot`

The core event handler that processes all drop operations.

```python
@rx.event
def handle_drop_to_slot(self, slot_type: str, position: int, item_data: dict):
    """
    Handles dropping an item into a specific slot.
    
    Args:
        slot_type: Type of slot (augment, shield, weapon, backpack, quick_use, safe_pocket)
        position: Position within slot type (0 for single slots, index for multi-slots)
        item_data: Data from the dragged item containing item_id, category, source info, etc.
    """
    item_id = item_data.get("item_id")
    source = item_data.get("source")
    
    item = self.get_item_by_id(item_id)
    if not item:
        return
    
    if not self._is_valid_drop(item["category"], slot_type):
        return
    
    # Clear source FIRST to avoid index shifting issues when moving within same list
    source_slot_type = item_data.get("source_slot_type")
    source_position = item_data.get("source_position")
    if source == "loadout" and source_slot_type and source_position is not None:
        # Only clear source if it's different from destination
        if not (source_slot_type == slot_type and source_position == position):
            # Adjust destination position if we're removing from same list before the destination
            if source_slot_type == slot_type and source_position < position:
                position = position - 1
            self._clear_source_slot(source_slot_type, source_position)
    
    # Now add to destination
    if slot_type in ["augment", "shield"]:
        self._drop_to_single_slot(slot_type, item_id, item_data)
    elif slot_type == "weapon":
        self._drop_to_weapon_slot(position, item_id, item_data)
    elif slot_type in ["backpack", "quick_use", "safe_pocket"]:
        self._drop_to_multi_slot(slot_type, position, item_id, item_data)
```

**Critical Implementation Details:**

1. **Order of Operations**: Clear source BEFORE adding to destination
   - Prevents index shifting bugs when moving within same list
   - Example: Moving quick_use[0] → quick_use[2] requires adjusting destination index

2. **Same-Slot Detection**: Skip operation if source == destination
   - Prevents unnecessary state mutations
   - Avoids edge case bugs

3. **Index Adjustment**: `position = position - 1` when source < destination
   - Compensates for list shrinking after removal
   - Essential for correct positioning

### Helper Methods

#### Validation

```python
def _is_valid_drop(self, item_category: str, slot_type: str) -> bool:
    """Validates if an item category can be dropped into a slot type."""
    drag_type = DRAG_TYPES.get(item_category)
    accepted_types = SLOT_ACCEPTANCE_RULES.get(slot_type, [])
    return drag_type in accepted_types if drag_type else False
```

#### Multi-Slot Handling

```python
def _drop_to_multi_slot(self, slot_type: str, position: int, item_id: str, item_data: dict):
    """Drops an item to a multi-item slot (backpack, quick_use, safe_pocket)."""
    if slot_type == "backpack":
        loadout_list = self.loadout_backpack
        max_position = 13
    elif slot_type == "quick_use":
        loadout_list = self.loadout_quick_use
        max_position = 3
    else:
        loadout_list = self.loadout_safe_pocket
        max_position = 1
    
    if position > max_position:
        return
    
    # Ensure list is long enough
    while len(loadout_list) <= position:
        loadout_list.append({"item_id": None, "quantity": 1, "tier": None})
    
    quantity = item_data.get("quantity", 1)
    tier = item_data.get("tier")
    
    item = self.get_item_by_id(item_id)
    if item and item["category"] != "Weapon":
        tier = None
    
    # Set the item at the specific position
    loadout_list[position] = {"item_id": item_id, "quantity": quantity, "tier": tier}
    
    # Clean up trailing None entries to avoid blank slots
    while loadout_list and loadout_list[-1]["item_id"] is None:
        loadout_list.pop()
```

**Key Feature**: Automatic cleanup of trailing `None` entries prevents blank slots from appearing in UI.

#### Source Clearing

```python
def _clear_source_slot(self, slot_type: str, position: int):
    """Clears the source slot when an item is moved from loadout to loadout."""
    if slot_type == "augment":
        self.loadout_augment = None
    elif slot_type == "shield":
        self.loadout_shield = None
    elif slot_type in ["weapon", "weapon_1", "weapon_2"]:
        # Handle both "weapon" with position and "weapon_1"/"weapon_2" slot names
        if slot_type == "weapon_1":
            self.loadout_weapon_1 = None
        elif slot_type == "weapon_2":
            self.loadout_weapon_2 = None
        elif slot_type == "weapon":
            if position == 0:
                self.loadout_weapon_1 = None
            elif position == 1:
                self.loadout_weapon_2 = None
    elif slot_type in ["backpack", "quick_use", "safe_pocket"]:
        if slot_type == "backpack":
            loadout_list = self.loadout_backpack
        elif slot_type == "quick_use":
            loadout_list = self.loadout_quick_use
        else:
            loadout_list = self.loadout_safe_pocket
        
        # Remove the item at this position
        if position < len(loadout_list):
            del loadout_list[position]
```

**Important**: Uses `del` to remove items, which shifts subsequent indices down by 1 (handled in main event handler).

---

## 3. Loadout Panel UI (`arc/components/loadout_panel.py`)

### Draggable Loadout Item

```python
def draggable_loadout_item(item: Item, slot_type: str, position: int, 
                          index: int | None = None, slot_size: str = "standard", 
                          quantity: int = 1, tier: int | None = None) -> rx.Component:
    """A draggable item that's already in the loadout."""
    drag_params = rxe.dnd.Draggable.collected_params
    
    # Size classes based on slot type
    if slot_size == "augment":
        size_class = "w-32 h-20"
    elif slot_size == "weapon":
        size_class = "w-[264px] h-40"
    else:  # standard
        size_class = "w-20 h-20"
    
    # Rarity-based border colors
    border_color = rx.match(
        item["rarity"],
        ("Common", "border-gray-400"),
        ("Uncommon", "border-green-500"),
        ("Rare", "border-blue-500"),
        ("Epic", "border-purple-500"),
        ("Legendary", "border-yellow-500"),
        "border-gray-400",
    )
    
    item_content = item_slot_with_item_content(
        item, slot_type, index, slot_size, quantity, tier, border_color
    )
    
    drag_type = DRAG_TYPES.get(item["category"], "ITEM_GEAR")
    
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
```

**Key Data Passed to Drop Handlers:**
- `source`: Always "loadout" for draggable items
- `source_slot_type`: Original slot type (for clearing)
- `source_position`: Original position (for clearing)
- `tier`: Weapon tier (preserved during moves)
- `quantity`: Item quantity (preserved during moves)

### Drop Target Pattern

```python
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
```

**Visual Feedback:**
- **Green border/background**: Valid drop (hover over compatible slot)
- **Red border/background**: Invalid drop (hover over incompatible slot)
- **Transparent**: Not hovering

**Critical Check**: `has_item` prevents rendering items with `item_id: None`, which would show as blank slots.

### Pre-compiled Slots (Avoiding rx.foreach)

```python
def backpack_section() -> rx.Component:
    """The Backpack section with a grid of slots."""
    return rx.el.div(
        rx.el.div(
            rx.el.h3("BACKPACK", class_name="text-sm font-bold text-gray-700 tracking-wide"),
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
                # ... slots 5-13
                columns="4",
                spacing="2",
            ),
        ),
        class_name="flex-[4] flex flex-col",
    )
```

**Why Pre-compiled?**
- Event handlers need concrete position values at compile time
- `rx.foreach` creates runtime loop variables that can't be captured in event handlers
- Solution: Pre-define all possible slots, control visibility with `rx.cond`

---

## 4. Main App Wrapper (`arc/arc.py`)

```python
import reflex_enterprise as rxe

def index() -> rx.Component:
    """The main page of the resource calculator."""
    return rxe.dnd.provider(
        rx.el.div(
            # ... page content
            loadout_panel(),
            # ... rest of app
        ),
        class_name="flex flex-col h-screen bg-white font-['Roboto']",
    )

app = rxe.App(
    theme=rx.theme(appearance="light"),
    head_components=[...],
)
```

**Critical**: Entire app must be wrapped in `rxe.dnd.provider` for drag-and-drop to function.

---

## 5. Item Cards - Click Only (`arc/components/item_card.py`)

```python
def item_card(item: Item, key: str | int | None = None) -> rx.Component:
    """A compact card that displays just the item image with hover popup.
    
    This is a click-only card (not draggable). Items in the loadout panel are draggable.
    """
    # ... UI code
    
    return rx.el.div(
        # ... card content
        on_click=lambda: CalculatorState.auto_equip_item(item["id"]),
        class_name=card_class,
    )
```

**Note**: No `rxe.dnd.draggable` wrapper. Sidebar items are click-only.

---

## Problems Encountered and Solutions

### Problem 1: TypedDict Incompatibility with rx.foreach + Draggable

**Symptom:**
```
VarAttributeError: The State var 'item' of type <class 'arc.state.Item'> 
has no attribute '_valid_parents' or may have been annotated wrongly.
```

**Root Cause:**
When `rx.foreach` iterates over a list of `TypedDict` items, it creates generic state variable proxies. When these proxies are passed to `rxe.dnd.draggable`, Reflex's component validation fails because the type information is lost.

**Attempted Solution 1: Convert TypedDict to Pydantic BaseModel**

Created `ItemModel(BaseModel)` and attempted to convert items:
```python
# FAILED - Various issues with Reflex proxy wrapping
all_items_models: list[ItemModel] = [ItemModel(**item) for item in ITEMS]
```

**Errors Encountered:**
- `TypeError: ItemModel() argument after ** must be a mapping, not list`
- `ValueError: dictionary update sequence element #0 has length 8; 2 is required`

**Why It Failed:**
- Pydantic's eager validation at class definition time conflicted with Reflex's lazy evaluation
- Reflex wraps state items in proxy objects that don't behave like standard Python dictionaries
- Converting within `@rx.var` computed properties introduced runtime proxy wrapping issues

**Final Solution: Hybrid Architecture**

Instead of trying to make sidebar items draggable:
1. Keep sidebar items as click-only (auto-equip functionality)
2. Make only loadout items draggable (BaseModel not required)
3. Users can rearrange via drag-and-drop within loadout
4. Users can add via click from sidebar

**Benefits:**
- ✅ Avoids TypedDict/Pydantic conversion complexity
- ✅ Simpler, more maintainable codebase
- ✅ Better UX: clicking is faster for initial adds
- ✅ Drag-and-drop where it matters most: rearranging loadout

### Problem 2: @rx.memo with State Variables

**Symptom:**
```
VarAttributeError: The State var 'arc.state.CalculatorState.loadout_augment_item' 
of type arc.state.Item | None has no attribute '_valid_parents'
```

**Root Cause:**
`@rx.memo` is incompatible with Reflex state variables passed as function parameters. Memoization attempts to cache based on parameter identity, but state variables are reactive and change identity.

**Solution:**
Remove `@rx.memo` from functions that receive state variables as parameters:
```python
# BEFORE (broken)
@rx.memo
def draggable_loadout_item(item: Item, ...):
    ...

# AFTER (working)
def draggable_loadout_item(item: Item, ...):
    ...
```

**Exception:**
`@rx.memo` can still be used with `rx.foreach` when the function doesn't need to directly access the iterated item as a parameter (e.g., in `dnd_demo.py` it works because the memoized function operates on constant data).

### Problem 3: Index Shifting When Moving Within Same List

**Symptom:**
Items would disappear or appear in wrong positions when dragging within the same section (e.g., quick_use[0] → quick_use[2]).

**Root Cause:**
Original implementation added to destination first, then cleared source:
```python
# BROKEN ORDER
self._drop_to_multi_slot(...)  # Add to destination
self._clear_source_slot(...)    # Remove from source
```

When moving within the same list, adding first created blank entries, then clearing removed the wrong item due to shifted indices.

**Solution:**
Reverse the order and adjust indices:
```python
# FIXED ORDER
# 1. Clear source first
if source_slot_type == slot_type and source_position < position:
    position = position - 1  # Adjust for list shrinkage
self._clear_source_slot(source_slot_type, source_position)

# 2. Then add to destination
self._drop_to_multi_slot(slot_type, position, item_id, item_data)
```

**Why This Works:**
- Clearing first removes the item from list, shifting all subsequent indices down
- Adjusting position compensates for this shift
- Example: Moving [A, B, C] index 0→2
  - Remove index 0: [B, C]
  - Adjust position: 2-1 = 1
  - Insert at index 1: [B, A, C] ✓

### Problem 4: Blank Items Appearing in UI

**Symptom:**
When dragging items to non-consecutive slots, blank items would appear in between.

**Root Cause:**
The `_drop_to_multi_slot` function padded lists with `{"item_id": None, ...}` entries, but the UI was rendering these as visible slots.

**Solution 1 (Backend):**
Clean up trailing `None` entries after every operation:
```python
# Clean up trailing None entries to avoid blank slots
while loadout_list and loadout_list[-1]["item_id"] is None:
    loadout_list.pop()
```

**Solution 2 (Frontend):**
Check for `None` items before rendering:
```python
has_item = (position < CalculatorState.loadout_backpack.length()) & (
    CalculatorState.loadout_backpack[position]["item_id"] != None
)

return rxe.dnd.drop_target(
    rx.cond(has_item, draggable_loadout_item(...), empty_slot("")),
    ...
)
```

### Problem 5: Python Ternary with Reflex State

**Symptom:**
```
VarTypeError: Cannot convert Var '(itemRxMemo?.["category"]?.valueOf?.() === "Weapon"?.valueOf?.())' 
to bool for use with `if`, `and`, `or`, and `not`. Instead use `rx.cond`
```

**Root Cause:**
Used Python's ternary operator with Reflex state variable:
```python
# BROKEN
"tier": selected_tier if item.category == "Weapon" else None
```

Reflex state variables compile to JavaScript and can't be evaluated at Python compile time.

**Solution:**
Use `rx.cond` for reactive conditionals:
```python
# FIXED
"tier": rx.cond(item.category == "Weapon", selected_tier, None)
```

---

## Key Learnings

### Reflex Enterprise DnD Limitations

1. **No rx.foreach with Draggable + TypedDict**
   - `rx.foreach` creates generic proxy objects that lose type information
   - Incompatible with `rxe.dnd.draggable` component validation
   - Workaround: Pre-compile components or use BaseModel (but BaseModel has its own issues)

2. **Event Handlers Need Concrete Values**
   - Lambda captures in `rx.foreach` don't work with loop variables
   - Event handlers compile to JavaScript and need concrete values
   - Solution: Pre-define all slots with `rx.cond` for visibility

3. **@rx.memo Restrictions**
   - Can't use with state variables as parameters
   - Reflex's reactive system conflicts with memoization
   - Only use for static/computed data

4. **Order of Operations Matters**
   - Clear before add to avoid index shifting
   - Adjust indices when removing from same list
   - Clean up trailing entries to avoid blank slots

### Best Practices

1. **Centralize Configuration**
   - Keep drag types and acceptance rules in one place
   - Easy to modify game logic without touching UI code

2. **Separate Concerns**
   - Click-to-add for simple operations (sidebar)
   - Drag-to-rearrange for complex operations (loadout)
   - Don't force drag-and-drop everywhere

3. **Visual Feedback**
   - Green = valid drop target
   - Red = invalid drop target
   - Clear, immediate user feedback prevents confusion

4. **Defensive Checks**
   - Always validate drop operations
   - Check for None items before rendering
   - Handle same-slot drops gracefully

5. **Index Management**
   - Account for list shrinkage when removing items
   - Clean up trailing None entries
   - Use del/pop carefully (both shift indices)

---

## Working Feature Set

### ✅ What Works

**Click-to-Add (Sidebar → Loadout):**
- Augment → Augment slot (or backpack if full)
- Shield → Shield slot (or backpack if full)
- Weapon → Weapon 1 → Weapon 2 → Backpack
- Healing/Trap → Quick Use → Safe Pocket → Backpack
- Gear/Gadget/Tool → Backpack

**Drag-to-Rearrange (Within Loadout):**
- Any item → Compatible slots (validated by acceptance rules)
- Items within same section (e.g., quick_use[0] → quick_use[2])
- Items between sections (e.g., backpack → weapon slot)
- Augments from backpack → augment slot
- Shields from backpack → shield slot
- Weapons between weapon slots and backpack
- Healing/Trap items → quick use, safe pocket, or backpack

**Visual Feedback:**
- Green border/background on valid drop targets
- Red border/background on invalid drop targets
- Smooth drag animations
- Clear slot highlighting

**State Preservation:**
- Weapon tiers maintained during moves
- Item quantities preserved
- No duplicate items
- Clean state after all operations

### ❌ What Doesn't Work (By Design)

- Dragging from sidebar (click-only by design)
- Using `rx.foreach` with draggable TypedDict items
- Passing state variables to `@rx.memo` functions

---

## Code Structure Summary

```
arc/
├── dnd_config.py              # Drag types and acceptance rules
├── state.py                   # Event handlers and state management
│   ├── handle_drop_to_slot()  # Main drop event handler
│   ├── _is_valid_drop()       # Validation
│   ├── _drop_to_single_slot() # Single slots (augment, shield)
│   ├── _drop_to_weapon_slot() # Weapon slots (with tier)
│   ├── _drop_to_multi_slot()  # Multi-item slots (backpack, etc)
│   └── _clear_source_slot()   # Source cleanup
├── components/
│   ├── item_card.py           # Click-only sidebar items
│   └── loadout_panel.py       # Draggable loadout items
│       ├── draggable_loadout_item()      # Draggable wrapper
│       ├── drop_target_augment()          # Augment drop target
│       ├── drop_target_shield()           # Shield drop target
│       ├── drop_target_weapon()           # Weapon drop targets
│       ├── drop_target_backpack_slot()    # Backpack drop targets
│       ├── drop_target_quick_use_slot()   # Quick use drop targets
│       └── drop_target_safe_pocket_slot() # Safe pocket drop targets
└── arc.py                     # App wrapper with rxe.dnd.provider
```

---

## Conclusion

The hybrid approach (click-to-add from sidebar, drag-to-rearrange in loadout) provides the best balance of:
- **Usability**: Fast item adding, flexible rearranging
- **Maintainability**: Clean code without TypedDict/BaseModel conversion
- **Reliability**: No proxy wrapping or memoization issues
- **Performance**: Efficient state updates with proper index management

The key lesson: **Don't fight the framework**. When Reflex's limitations made sidebar drag-and-drop problematic, pivoting to a hybrid approach delivered better UX with cleaner code.

