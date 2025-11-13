# Drag-and-Drop Implementation Summary

## Overview

Successfully implemented comprehensive drag-and-drop functionality for the Arc Raiders Loadout Calculator. Users can now drag items from the item selector into loadout slots, drag items between loadout slots, and receive visual feedback about valid/invalid drop targets.

## Implementation Date

November 13, 2025

## What Was Implemented

### 1. Configuration & State Management (`arc/dnd_config.py`, `arc/state.py`)

#### Created DnD Configuration Constants
- **`DRAG_TYPES`**: Maps item categories to drag type identifiers
  - Weapon → ITEM_WEAPON
  - Augment → ITEM_AUGMENT
  - Shield → ITEM_SHIELD
  - Healing → ITEM_HEALING
  - Trap → ITEM_TRAP
  - Gear, Gadget, Tool → ITEM_GEAR, ITEM_GADGET, ITEM_TOOL

- **`SLOT_ACCEPTANCE_RULES`**: Defines which drag types each slot accepts
  - Augment slot: Only augments
  - Shield slot: Only shields
  - Weapon slots: Only weapons
  - Backpack: Weapons, healing, traps, gear, gadgets, tools
  - Quick use: Only healing and traps
  - Safe pocket: Only healing and traps

#### Created LoadoutSlot Model
```python
class LoadoutSlot(rx.Base):
    item_id: str | None = None
    quantity: int = 1
    tier: int | None = None
    slot_type: SlotType = "backpack"
    position: int = 0
```

#### Added Drag-and-Drop Event Handlers
- `get_item_by_id()`: Helper to retrieve items by ID
- `_is_valid_drop()`: Validates if an item can be dropped in a slot
- `handle_drop_to_slot()`: Main drop handler that routes to specific slot handlers
- `_drop_to_single_slot()`: Handles augment/shield drops
- `_drop_to_weapon_slot()`: Handles weapon slot drops with tier preservation
- `_drop_to_multi_slot()`: Handles backpack/quick use/safe pocket drops
- `_clear_source_slot()`: Clears source slot when moving items between loadout slots

### 2. Draggable Item Cards (`arc/components/item_card.py`)

- Added `@rx.memo` decorator for performance
- Wrapped item cards with `rxe.dnd.draggable()`
- Added visual feedback:
  - Blue transparent background when dragging
  - 50% opacity while being dragged
- Item data passed includes:
  - `item_id`: The item's unique identifier
  - `category`: Item category for validation
  - `source`: "item_selector" to track origin
  - `tier`: Current tier for weapons

### 3. Drop Target Slots (`arc/components/loadout_panel.py`)

#### Created Draggable Loadout Items
- `draggable_loadout_item()`: Makes items in loadout draggable to other slots
- Passes source slot information for move operations
- Preserves tier and quantity when dragging

#### Equipment Section
- `drop_target_augment()`: Drop target for augment slot
- `drop_target_shield()`: Drop target for shield slot  
- `drop_target_weapon(position)`: Drop targets for weapon slots 1 and 2

#### Multi-Slot Sections
- `drop_target_backpack_slot(position)`: 14 pre-compiled backpack slots (0-13)
- `drop_target_quick_use_slot(position)`: 4 pre-compiled quick use slots (0-3)
- `drop_target_safe_pocket_slot(position)`: 2 pre-compiled safe pocket slots (0-1)

#### Visual Feedback
All drop targets show:
- **Green border + light green background**: Valid drop (item can be placed here)
- **Red border + light red background**: Invalid drop (item cannot be placed here)
- **Transparent border**: No hover state

#### Pre-compilation Strategy
Following lessons from `dnd_demo.py`, all slots are pre-compiled with concrete position values:

```python
rx.grid(
    drop_target_backpack_slot(0),
    rx.cond(State.max_backpack_slots >= 2, drop_target_backpack_slot(1)),
    rx.cond(State.max_backpack_slots >= 3, drop_target_backpack_slot(2)),
    # ... up to 14
)
```

This approach:
- Compiles all slots at build time with concrete position integers
- Uses `rx.cond()` to show/hide slots based on augment limits at runtime
- Avoids `rx.foreach` with event handlers (which causes compilation errors)

### 4. App Integration (`arc/arc.py`)

- Wrapped entire application in `rxe.dnd.provider()`
- Ensures drag-and-drop context is available throughout the app

## Key Features

### Drag from Item Selector
- Click and drag any item from the item selector
- Visual feedback (blue tint, reduced opacity) while dragging
- Automatically uses the selected tier for weapons

### Drop into Loadout Slots
- Drop items into any compatible slot
- Visual feedback shows valid (green) vs invalid (red) targets
- Invalid drops are prevented (e.g., can't drop weapon in augment slot)
- Replaces existing item if slot is occupied

### Drag Between Loadout Slots
- Drag items from one loadout slot to another
- Source slot is cleared when item is moved
- Tier and quantity are preserved during moves
- Can move weapons from weapon slot to backpack, etc.

### Preserved Click Functionality
- Clicking items still auto-equips them (as before)
- Drag-and-drop is an additional interaction method
- Both methods work seamlessly together

## Technical Implementation Details

### Drag Types & Validation
- Each item category maps to a unique drag type
- Drop targets specify which drag types they accept
- Validation happens both in UI (visual feedback) and backend (event handler)

### Position Tracking
- Every slot knows its position (0-indexed)
- Position info passed in drag data for source tracking
- Enables proper clearing of source slots during moves

### State Preservation
- Weapon tiers preserved when dragging from selector (uses selected tier)
- Weapon tiers preserved when moving between loadout slots
- Item quantities preserved for stackable items
- No data loss during drag operations

### Dynamic Slot Visibility
- Backpack: 14 possible slots, visibility controlled by augment
- Quick use: 4 possible slots, visibility controlled by augment
- Safe pocket: 0-2 possible slots, visibility controlled by augment
- All slots pre-compiled, `rx.cond()` controls rendering

## Files Modified

1. **`arc/dnd_config.py`** (NEW)
   - Drag type constants
   - Slot acceptance rules

2. **`arc/state.py`**
   - Added `LoadoutSlot` model
   - Added drag-and-drop event handlers
   - Added validation logic

3. **`arc/components/item_card.py`**
   - Made item cards draggable
   - Added visual feedback

4. **`arc/components/loadout_panel.py`**
   - Created drop target slots for all loadout areas
   - Added draggable loadout items
   - Implemented visual feedback for drop targets

5. **`arc/arc.py`**
   - Wrapped app in DnD provider

## Testing Recommendations

### Basic Functionality
- [x] Drag weapon from selector to weapon slot 1
- [x] Drag weapon from selector to weapon slot 2
- [x] Drag augment from selector to augment slot
- [x] Drag shield from selector to shield slot
- [x] Drag healing item to quick use
- [x] Drag trap to quick use
- [x] Drag items to backpack

### Invalid Drops
- [x] Try dragging weapon to augment slot (should show red)
- [x] Try dragging augment to weapon slot (should show red)
- [x] Try dragging weapon to quick use (should show red)
- [x] Try dragging gear to quick use (should show red)

### Slot-to-Slot Moves
- [x] Drag weapon from weapon 1 to weapon 2
- [x] Drag weapon from weapon slot to backpack
- [x] Drag item from backpack to quick use (if compatible)
- [x] Drag item from quick use to safe pocket

### State Preservation
- [x] Set weapon to tier 3, drag to loadout, verify tier preserved
- [x] Move weapon between slots, verify tier preserved
- [x] Change quantity of stackable item, move it, verify quantity preserved

### Dynamic Slots
- [x] Change augment to one with different slot counts
- [x] Verify correct number of slots shown
- [x] Verify items beyond limit are hidden but preserved

### Edge Cases
- [x] Drag item and release outside any drop zone (returns to source)
- [x] Drag item over occupied slot (replaces item)
- [x] Rapid dragging multiple items
- [x] Drag while search/filter active

## Known Limitations & Future Enhancements

### Current Limitations
1. Dropping on occupied slot replaces the item (doesn't swap)
2. Cannot select multiple items for batch operations
3. No custom drag preview (uses default browser behavior)

### Future Enhancements (Not Implemented)
1. **Swap Instead of Replace**: When dropping on occupied slot, swap the items
2. **Multi-select Drag**: Ctrl+Click to select multiple, drag all at once
3. **Undo/Redo**: Track drag-and-drop operations for undo
4. **Tooltips on Hover**: Show why a drop is invalid (e.g., "Weapons cannot be placed in Quick Use slots")
5. **Animations**: Smooth transitions when items move
6. **Touch Support**: Test and optimize for mobile/tablet devices
7. **Drag Preview Customization**: Custom preview showing item with tier/quantity

## Conclusion

The drag-and-drop implementation is complete and fully functional. All 7 phases were successfully implemented:

1. ✅ Phase 1: Created LoadoutSlot model and updated state structure
2. ✅ Phase 2: Created DnD config constants
3. ✅ Phase 3: Made item selector cards draggable
4. ✅ Phase 4: Converted loadout slots to drop targets with visual feedback
5. ✅ Phase 5: Implemented drop handler logic
6. ✅ Phase 6: Made loadout items draggable (for slot-to-slot moves)
7. ✅ Phase 7: Wrapped app in DnD provider

The implementation follows Reflex Enterprise best practices, uses the pre-compilation pattern discovered in the demo, and provides excellent visual feedback to users. The existing click-to-equip functionality is preserved, giving users two ways to build their loadout.

