# Arc Raiders Loadout: Drag-and-Drop Implementation Plan

## Executive Summary

This document outlines the comprehensive approach for implementing drag-and-drop functionality in the Arc Raiders resource calculator, building on lessons learned from the `dnd_demo.py` proof-of-concept. The implementation will allow users to drag items from the item selector into loadout slots, drag items between slots, and receive visual feedback about valid/invalid drop targets.

---

## 1. Lessons Learned from Demo

### 1.1 Key Technical Discoveries

From our work in `dnd_demo.py` and `reflex_dnd_solution.md`, we discovered critical patterns for working with Reflex Enterprise drag-and-drop:

#### ✅ What Works: Pre-compiled Drop Zones

```python
def drop_zone(position: int):  # position is a concrete Python int
    params = rxe.dnd.DropTarget.collected_params
    return rxe.dnd.drop_target(
        rx.cond(
            State.item_position == position,
            draggable_item(),
            empty_slot_display(),
        ),
        accept=["ItemType"],
        on_drop=lambda _: State.move_to_position(position),
        border_color=rx.cond(params.is_over, "green", "gray.300"),
    )

# Show/hide zones based on dynamic state
rx.cond(State.num_slots >= 1, drop_zone(0)),
rx.cond(State.num_slots >= 2, drop_zone(1)),
```

**Why this works:**
- Each `drop_zone(0)`, `drop_zone(1)` is called with a concrete Python `int`
- The lambda captures this concrete value at compile time
- All drop zones are pre-compiled into JavaScript
- `rx.cond()` controls visibility at runtime without re-compilation

#### ❌ What Doesn't Work: Dynamic Loop Variables in Event Handlers

```python
# This pattern FAILS
rx.foreach(
    rx.Var.range(num_slots),
    lambda position_var: drop_zone_with_handler(position_var)
)

def drop_zone_with_handler(position_var):
    return rxe.dnd.drop_target(
        ...,
        on_drop=lambda item: State.handle_drop(position_var),  # Compile-time error
    )
```

**Why this fails:**
- Event handlers compile to JavaScript at build time
- `position_var` from `rx.foreach` is a reactive `Var[int]` with no value until runtime
- Results in JavaScript errors: `ReferenceError: i_rx_state_ is not defined`

### 1.2 Collected Parameters for Visual Feedback

The `collected_params` API provides real-time drag/drop state:

```python
# In draggable component
drag_params = rxe.dnd.Draggable.collected_params
# Available: is_dragging, can_drag

# In drop target
drop_params = rxe.dnd.DropTarget.collected_params
# Available: is_over, can_drop, item (the dragged item data)
```

This enables rich visual feedback without additional state management.

---

## 2. Current State Architecture Analysis

### 2.1 Existing State Structure

The current implementation has **inconsistent state storage** across slot types:

```python
class CalculatorState(rx.State):
    # Single-item slots: Just item ID
    loadout_augment: str | None = None
    loadout_shield: str | None = None
    
    # Weapon slots: Dict with metadata
    loadout_weapon_1: dict[str, int | str | None] | None = None
    loadout_weapon_2: dict[str, int | str | None] | None = None
    # Structure: {"item_id": str, "quantity": int, "tier": int | None}
    
    # Multi-item slots: List of dicts
    loadout_backpack: list[dict[str, int | str | None]] = []
    loadout_quick_use: list[dict[str, int | str | None]] = []
    loadout_safe_pocket: list[dict[str, int | str | None]] = []
```

### 2.2 Problems with Current Structure

1. **Inconsistency**: Augment/shield use plain strings, weapons use dicts
2. **Type Ambiguity**: `dict[str, int | str | None]` is not type-safe
3. **Quantity/Tier Confusion**: Augment/shield don't have quantity, but use same dict structure elsewhere
4. **No Position Tracking**: Multi-item lists don't explicitly track "slot position"

---

## 3. Proposed State Management Approach

### 3.1 Unified LoadoutSlot Model

**Recommendation:** Create a consistent, type-safe model for ALL loadout slots.

```python
from typing import Literal

class LoadoutSlot(rx.Base):
    """Represents a single loadout slot with optional item."""
    item_id: str | None = None
    quantity: int = 1
    tier: int | None = None
    slot_type: Literal["augment", "shield", "weapon", "backpack", "quick_use", "safe_pocket"]
    position: int  # Position within multi-slot areas (0-indexed)

class CalculatorState(rx.State):
    # Single slots: Always one slot, may be empty (item_id=None)
    loadout_augment: LoadoutSlot = LoadoutSlot(slot_type="augment", position=0)
    loadout_shield: LoadoutSlot = LoadoutSlot(slot_type="shield", position=0)
    loadout_weapon_1: LoadoutSlot = LoadoutSlot(slot_type="weapon", position=0)
    loadout_weapon_2: LoadoutSlot = LoadoutSlot(slot_type="weapon", position=1)
    
    # Multi-slot areas: Fixed-size list (max slots), empty slots have item_id=None
    loadout_backpack: list[LoadoutSlot] = []
    loadout_quick_use: list[LoadoutSlot] = []
    loadout_safe_pocket: list[LoadoutSlot] = []
```

### 3.2 Why This Structure?

**Benefits:**

1. **Type Safety**: Clear, typed structure for all slots
2. **Consistency**: Same data model everywhere
3. **Position Awareness**: Every slot knows its position
4. **Empty vs. Occupied**: `item_id=None` clearly indicates empty slot
5. **Drag-and-Drop Ready**: Position tracking makes slot-to-slot moves trivial
6. **Future-Proof**: Easy to add new properties (e.g., enchantments, durability)

### 3.3 Initialization Pattern

For dynamic multi-slot areas, initialize with empty slots up to maximum:

```python
@rx.event
def initialize_loadout_slots(self):
    """Initialize all loadout slots with empty placeholders."""
    # Create 14 empty backpack slots
    self.loadout_backpack = [
        LoadoutSlot(slot_type="backpack", position=i)
        for i in range(14)
    ]
    
    # Create 4 empty quick use slots
    self.loadout_quick_use = [
        LoadoutSlot(slot_type="quick_use", position=i)
        for i in range(4)
    ]
    
    # Create 2 empty safe pocket slots
    self.loadout_safe_pocket = [
        LoadoutSlot(slot_type="safe_pocket", position=i)
        for i in range(2)
    ]
```

**Key Insight:** We're not creating/destroying slots dynamically - all slots always exist, we just hide the ones beyond the augment's limits using `rx.cond()`.

---

## 4. Drag-and-Drop Implementation Strategy

### 4.1 Draggable Item Types

Define drag types corresponding to item categories:

```python
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
```

### 4.2 Drop Target Acceptance Rules

Each slot type accepts specific item categories:

```python
SLOT_ACCEPTANCE_RULES = {
    "augment": ["ITEM_AUGMENT"],
    "shield": ["ITEM_SHIELD"],
    "weapon": ["ITEM_WEAPON"],
    "backpack": ["ITEM_WEAPON", "ITEM_HEALING", "ITEM_TRAP", "ITEM_GEAR", "ITEM_GADGET", "ITEM_TOOL"],
    "quick_use": ["ITEM_HEALING", "ITEM_TRAP"],
    "safe_pocket": ["ITEM_HEALING", "ITEM_TRAP"],
}
```

### 4.3 Draggable Item Component

Items in the sidebar item selector should be draggable:

```python
@rx.memo
def draggable_item_card(item: Item):
    """A draggable item card from the item selector."""
    drag_params = rxe.dnd.Draggable.collected_params
    
    return rxe.dnd.draggable(
        rx.card(
            # Item display (image, name, etc.)
            rx.image(src=item["image"], alt=item["name"]),
            rx.text(item["name"], weight="bold"),
            # ... more content
            
            # Visual feedback when dragging
            opacity=rx.cond(drag_params.is_dragging, 0.5, 1.0),
            bg=rx.cond(drag_params.is_dragging, "blue.100", "white"),
        ),
        type=DRAG_TYPES[item["category"]],
        item={
            "item_id": item["id"],
            "category": item["category"],
            "source": "item_selector",  # Track where drag originated
        },
        on_end=lambda: None,  # Optional: could show toast on drop
    )
```

### 4.4 Draggable Loadout Item Component

Items already in loadout should also be draggable to other slots:

```python
@rx.memo
def draggable_loadout_item(slot: LoadoutSlot, item: Item):
    """A draggable item that's already in the loadout."""
    drag_params = rxe.dnd.Draggable.collected_params
    
    return rxe.dnd.draggable(
        # Item display with tier/quantity controls
        rx.box(
            rx.image(src=item["image"], alt=item["name"]),
            # Include tier selector or quantity controls
            # ...
            
            # Visual feedback
            opacity=rx.cond(drag_params.is_dragging, 0.3, 1.0),
            border=rx.cond(drag_params.is_dragging, "2px dashed gray", f"2px solid {border_color}"),
        ),
        type=DRAG_TYPES[item["category"]],
        item={
            "item_id": item["id"],
            "category": item["category"],
            "source": "loadout",
            "source_slot_type": slot.slot_type,
            "source_position": slot.position,
            "tier": slot.tier,
            "quantity": slot.quantity,
        },
    )
```

### 4.5 Drop Target Slots

#### Single-Item Slots (Augment, Shield, Weapons)

```python
def drop_target_augment_slot():
    """Drop target for the augment slot."""
    drop_params = rxe.dnd.DropTarget.collected_params
    
    return rxe.dnd.drop_target(
        rx.cond(
            CalculatorState.loadout_augment.item_id,
            draggable_loadout_item(
                CalculatorState.loadout_augment,
                CalculatorState.loadout_augment_item
            ),
            empty_slot("Augment", slot_size="augment"),
        ),
        accept=SLOT_ACCEPTANCE_RULES["augment"],
        on_drop=lambda item: CalculatorState.handle_drop_to_slot("augment", 0, item),
        
        # Visual feedback
        border_color=rx.cond(
            drop_params.is_over & drop_params.can_drop,
            "green.500",  # Valid drop
            rx.cond(
                drop_params.is_over,
                "red.500",  # Invalid drop
                "gray.300"  # Not hovering
            )
        ),
        bg=rx.cond(
            drop_params.is_over & drop_params.can_drop,
            "green.50",
            rx.cond(drop_params.is_over, "red.50", "transparent")
        ),
        
        width="128px",
        height="80px",
        class_name="rounded-lg",
    )
```

#### Multi-Item Slots (Backpack)

```python
def drop_target_backpack_slot(position: int):
    """Drop target for a specific backpack slot position."""
    drop_params = rxe.dnd.DropTarget.collected_params
    
    return rxe.dnd.drop_target(
        rx.cond(
            CalculatorState.loadout_backpack[position].item_id,
            draggable_loadout_item(
                CalculatorState.loadout_backpack[position],
                CalculatorState.get_item_by_id(
                    CalculatorState.loadout_backpack[position].item_id
                )
            ),
            empty_slot("", slot_size="standard"),
        ),
        accept=SLOT_ACCEPTANCE_RULES["backpack"],
        on_drop=lambda item: CalculatorState.handle_drop_to_slot("backpack", position, item),
        
        # Visual feedback (same as above)
        border_color=rx.cond(
            drop_params.is_over & drop_params.can_drop,
            "green.500",
            rx.cond(drop_params.is_over, "red.500", "gray.300")
        ),
        bg=rx.cond(
            drop_params.is_over & drop_params.can_drop,
            "green.50",
            rx.cond(drop_params.is_over, "red.50", "transparent")
        ),
        
        width="80px",
        height="80px",
        class_name="rounded-lg",
    )

def backpack_section():
    """Backpack grid with pre-compiled drop zones."""
    return rx.el.div(
        rx.el.h3("BACKPACK", class_name="..."),
        
        # Pre-compile all 14 possible slots
        rx.grid(
            drop_target_backpack_slot(0),
            rx.cond(CalculatorState.max_backpack_slots >= 2, drop_target_backpack_slot(1)),
            rx.cond(CalculatorState.max_backpack_slots >= 3, drop_target_backpack_slot(2)),
            rx.cond(CalculatorState.max_backpack_slots >= 4, drop_target_backpack_slot(3)),
            # ... up to 14
            columns="4",
            gap="2",
        ),
    )
```

### 4.6 Drop Handler Logic

Central drop handler that processes all drag-and-drop operations:

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
    source = item_data.get("source")  # "item_selector" or "loadout"
    
    # Get the item object
    item = next((i for i in self.all_items if i["id"] == item_id), None)
    if not item:
        return
    
    # Validate that this item can go in this slot type
    if not self._is_valid_drop(item["category"], slot_type):
        return rx.toast.error(f"Cannot place {item['category']} in {slot_type} slot")
    
    # Handle different slot types
    if slot_type in ["augment", "shield"]:
        self._drop_to_single_slot(slot_type, item_id, item_data)
    
    elif slot_type in ["weapon"]:
        self._drop_to_weapon_slot(position, item_id, item_data)
    
    elif slot_type in ["backpack", "quick_use", "safe_pocket"]:
        self._drop_to_multi_slot(slot_type, position, item_id, item_data)
    
    # If source was loadout, clear the source slot
    if source == "loadout":
        source_slot_type = item_data.get("source_slot_type")
        source_position = item_data.get("source_position")
        if source_slot_type and source_position is not None:
            self._clear_source_slot(source_slot_type, source_position)

def _is_valid_drop(self, item_category: str, slot_type: str) -> bool:
    """Validates if an item category can be dropped into a slot type."""
    drag_type = DRAG_TYPES.get(item_category)
    accepted_types = SLOT_ACCEPTANCE_RULES.get(slot_type, [])
    return drag_type in accepted_types

def _drop_to_single_slot(self, slot_type: str, item_id: str, item_data: dict):
    """Drops an item to augment or shield slot."""
    if slot_type == "augment":
        self.loadout_augment.item_id = item_id
    elif slot_type == "shield":
        self.loadout_shield.item_id = item_id

def _drop_to_weapon_slot(self, position: int, item_id: str, item_data: dict):
    """Drops a weapon to weapon slot 1 or 2."""
    tier = item_data.get("tier", self.selected_weapon_tiers.get(item_id, 1))
    
    if position == 0:
        self.loadout_weapon_1.item_id = item_id
        self.loadout_weapon_1.tier = tier
    elif position == 1:
        self.loadout_weapon_2.item_id = item_id
        self.loadout_weapon_2.tier = tier

def _drop_to_multi_slot(self, slot_type: str, position: int, item_id: str, item_data: dict):
    """Drops an item to a multi-item slot (backpack, quick_use, safe_pocket)."""
    loadout_list = getattr(self, f"loadout_{slot_type}")
    
    # Ensure list is initialized with enough empty slots
    while len(loadout_list) <= position:
        loadout_list.append(LoadoutSlot(slot_type=slot_type, position=len(loadout_list)))
    
    # Set the item in the target position
    loadout_list[position].item_id = item_id
    loadout_list[position].quantity = item_data.get("quantity", 1)
    loadout_list[position].tier = item_data.get("tier")

def _clear_source_slot(self, slot_type: str, position: int):
    """Clears the source slot when an item is moved from loadout to loadout."""
    if slot_type in ["augment", "shield"]:
        slot = getattr(self, f"loadout_{slot_type}")
        slot.item_id = None
    
    elif slot_type == "weapon":
        if position == 0:
            self.loadout_weapon_1.item_id = None
        elif position == 1:
            self.loadout_weapon_2.item_id = None
    
    elif slot_type in ["backpack", "quick_use", "safe_pocket"]:
        loadout_list = getattr(self, f"loadout_{slot_type}")
        if position < len(loadout_list):
            loadout_list[position].item_id = None
```

### 4.7 Visual Feedback: Floating Item Preview

The "floating item" that follows the cursor should change color based on validity:

```python
@rx.memo
def draggable_item_with_feedback(item: Item):
    """Draggable item with visual feedback for valid/invalid drops."""
    drag_params = rxe.dnd.Draggable.collected_params
    
    # Note: We can't directly detect "hovering over invalid slot" from the draggable side
    # Instead, the drop target provides visual feedback via border_color/bg
    
    return rxe.dnd.draggable(
        rx.box(
            rx.image(src=item["image"], width="60px", height="60px"),
            # Blue transparent background when dragging
            bg=rx.cond(drag_params.is_dragging, "rgba(59, 130, 246, 0.2)", "white"),
            border="2px solid",
            border_color=rx.cond(drag_params.is_dragging, "blue.500", "gray.300"),
            border_radius="8px",
            padding="4px",
        ),
        type=DRAG_TYPES[item["category"]],
        item={"item_id": item["id"], "category": item["category"], "source": "item_selector"},
    )
```

**Important Note:** The Reflex Enterprise DnD library doesn't provide a built-in way for the draggable component to know if it's hovering over a valid vs. invalid drop target. The `can_drop` parameter is only available in `DropTarget.collected_params`, not `Draggable.collected_params`.

**Solution:** Use **drop target visual feedback** (changing slot border/background colors) rather than changing the floating item color. This is actually clearer UX - the user sees which slot will receive the item.

---

## 5. Implementation Checklist

### Phase 1: State Migration
- [ ] Create `LoadoutSlot` model in `state.py`
- [ ] Add `DRAG_TYPES` and `SLOT_ACCEPTANCE_RULES` constants
- [ ] Update `CalculatorState` to use unified slot structure
- [ ] Add `initialize_loadout_slots()` method
- [ ] Migrate existing state access to new structure
- [ ] Update all computed vars (`loadout_augment_item`, etc.) for new structure

### Phase 2: Draggable Items
- [ ] Wrap item cards in item selector with `rxe.dnd.draggable()`
- [ ] Add `@rx.memo` decorator to draggable item component
- [ ] Pass item metadata in `item` parameter
- [ ] Add visual feedback for dragging state

### Phase 3: Drop Targets
- [ ] Convert augment slot to drop target
- [ ] Convert shield slot to drop target
- [ ] Convert weapon slots to drop targets
- [ ] Pre-compile all 14 backpack drop targets with `rx.cond()` visibility
- [ ] Pre-compile all 4 quick use drop targets
- [ ] Pre-compile all 2 safe pocket drop targets
- [ ] Add visual feedback (border colors, background colors) using `collected_params`

### Phase 4: Drop Handlers
- [ ] Implement `handle_drop_to_slot()` central handler
- [ ] Implement `_is_valid_drop()` validation
- [ ] Implement `_drop_to_single_slot()`
- [ ] Implement `_drop_to_weapon_slot()`
- [ ] Implement `_drop_to_multi_slot()`
- [ ] Implement `_clear_source_slot()` for loadout-to-loadout moves

### Phase 5: Draggable Loadout Items
- [ ] Wrap items in loadout with `rxe.dnd.draggable()`
- [ ] Pass source slot information in drag item data
- [ ] Preserve tier/quantity when dragging from loadout

### Phase 6: App Provider
- [ ] Wrap entire app in `rxe.dnd.provider()`
- [ ] Test drag-and-drop functionality
- [ ] Verify click-to-equip still works alongside drag-and-drop

### Phase 7: Polish & Edge Cases
- [ ] Add toast notifications for invalid drops
- [ ] Handle rapid dragging/multiple simultaneous users
- [ ] Add "Are you sure?" for replacing occupied slots
- [ ] Test with different augments changing max slots
- [ ] Verify tier persistence when moving weapons
- [ ] Verify quantity persistence when moving stackable items

---

## 6. Migration Path from Current State

Since the current state structure is inconsistent, here's a migration strategy:

### Option A: Big Bang Migration (Recommended)

1. Create new `LoadoutSlot` model
2. Update all state variables at once
3. Update all component accessors in one PR
4. Test thoroughly before merging

**Pros:** Clean break, no dual systems
**Cons:** More risky, larger PR

### Option B: Gradual Migration

1. Create `LoadoutSlot` model alongside existing state
2. Add compatibility methods that read/write to both
3. Migrate components one at a time
4. Remove old state structure once all components migrated

**Pros:** Lower risk, easier to test incrementally
**Cons:** Temporary code duplication, more complex during transition

**Recommendation:** Given the relatively small codebase, **Option A (Big Bang)** is preferable. The codebase is small enough to test comprehensively, and avoiding dual systems will keep the code cleaner.

---

## 7. Advanced Features (Future Enhancements)

### 7.1 Swap Instead of Replace

Currently, dropping an item on an occupied slot replaces it. Future enhancement: **swap** the items.

```python
def _drop_to_multi_slot(self, slot_type: str, position: int, item_id: str, item_data: dict):
    """Drops with swap logic."""
    loadout_list = getattr(self, f"loadout_{slot_type}")
    target_slot = loadout_list[position]
    
    # If target is occupied and source is loadout, swap
    if target_slot.item_id and item_data.get("source") == "loadout":
        source_slot_type = item_data["source_slot_type"]
        source_position = item_data["source_position"]
        
        # Store target item
        target_item_id = target_slot.item_id
        target_tier = target_slot.tier
        target_quantity = target_slot.quantity
        
        # Place dragged item in target
        target_slot.item_id = item_id
        target_slot.tier = item_data.get("tier")
        target_slot.quantity = item_data.get("quantity", 1)
        
        # Place target item in source
        source_list = getattr(self, f"loadout_{source_slot_type}")
        source_list[source_position].item_id = target_item_id
        source_list[source_position].tier = target_tier
        source_list[source_position].quantity = target_quantity
    else:
        # Normal replacement
        target_slot.item_id = item_id
        # ...
```

### 7.2 Drag Preview Customization

Use `preview_options` to customize the drag preview:

```python
rxe.dnd.draggable(
    # ... component
    preview_options={
        "anchorX": 0.5,
        "anchorY": 0.5,
        "captureDraggingState": True,
    },
)
```

### 7.3 Multi-Select Drag (Advanced)

Allow dragging multiple items at once (e.g., Ctrl+Click to select, then drag all):

```python
selected_items: set[str] = set()  # Track selected item IDs

def handle_drop_multi(self, slot_type: str, position: int, item_data: dict):
    """Drop multiple items starting at position."""
    if self.selected_items:
        for i, item_id in enumerate(self.selected_items):
            self._drop_to_multi_slot(slot_type, position + i, item_id, {})
```

---

## 8. Testing Strategy

### 8.1 Manual Test Cases

1. **Basic Drag from Selector**
   - Drag augment to augment slot
   - Drag weapon to weapon slot
   - Drag healing item to quick use slot

2. **Invalid Drops**
   - Try dragging weapon to augment slot (should show red)
   - Try dragging healing item to weapon slot (should show red)

3. **Loadout to Loadout**
   - Drag weapon from weapon 1 to weapon 2
   - Drag item from backpack to quick use
   - Drag item from quick use to safe pocket

4. **Replacing Items**
   - Drag new augment over existing augment (should replace)
   - Drag weapon over existing weapon (should replace)

5. **Dynamic Slot Count**
   - Change augment (changes max slots)
   - Verify slots beyond max are hidden
   - Verify items in hidden slots are preserved

6. **Tier/Quantity Preservation**
   - Drag tier 3 weapon to backpack, verify tier preserved
   - Drag item with quantity 3 to different slot, verify quantity preserved

### 8.2 Edge Cases

- Drag item and release outside any drop zone (should return to source)
- Rapid dragging (multiple items quickly)
- Drag while search filter active
- Drag while category filter active
- Drag with empty loadout
- Drag with full backpack (all 14 slots)

---

## 9. Code Organization

Recommended file structure for drag-and-drop code:

```
arc/
  state.py                  # LoadoutSlot model, CalculatorState with DnD methods
  components/
    item_card.py           # Draggable item cards for selector
    loadout_panel.py       # Drop target slots, draggable loadout items
    dnd_config.py          # DRAG_TYPES, SLOT_ACCEPTANCE_RULES constants
```

---

## 10. Conclusion

This implementation plan provides a comprehensive, type-safe approach to adding drag-and-drop to the Arc Raiders resource calculator. By:

1. **Unifying state structure** with `LoadoutSlot` model
2. **Pre-compiling drop zones** with concrete positions
3. **Using collected parameters** for visual feedback
4. **Centralizing drop logic** in a single handler

We create a maintainable, extensible system that supports the current requirements and future enhancements. The approach builds directly on the lessons learned from `dnd_demo.py` and aligns with Reflex Enterprise best practices.

The migration to this structure will require updates across multiple files, but the resulting codebase will be significantly cleaner, more type-safe, and easier to maintain going forward.

