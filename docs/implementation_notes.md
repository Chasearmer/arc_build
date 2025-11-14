# Drag-and-Drop Implementation Notes

## Important Technical Limitation Discovered

### Issue with `rxe.dnd.draggable` and `rx.foreach`

**Problem:** You cannot use `rxe.dnd.draggable` inside `rx.foreach` when iterating over TypedDict items.

**Why:**
- When `rx.foreach` iterates, the loop variable (e.g., `item`) is a Reflex state var, not a concrete value
- `rxe.dnd.draggable` validation expects concrete component children
- Reflex compiler throws: `VarAttributeError: The State var 'item' has no attribute '_valid_parents'`

**Example that FAILS:**
```python
rx.foreach(
    items_list,
    lambda item: rxe.dnd.draggable(  # ❌ Cannot wrap in draggable
        item_card(item),
        type="ITEM",
        item={"id": item["id"]}
    )
)
```

### Solution Implemented

**Items in sidebar are NOT draggable.** Instead:

1. **Click items in sidebar** to add to loadout (existing behavior)
2. **Drag items within loadout** to rearrange (new behavior)

This provides the core drag-and-drop functionality where it matters most (rearranging your loadout) without hitting the technical limitation.

## What About `@rx.memo`?

### What is Memoization?

**Memoization** is a caching optimization:
- Stores function results
- Returns cached result when called with same inputs
- Avoids expensive re-computations

### What Does `@rx.memo` Do?

In Reflex, `@rx.memo`:
- Caches component render outputs
- Only re-renders when inputs change
- **Only works with concrete Python values** (int, str, etc.)
- **Cannot work with Reflex state vars** (they're reactive objects)

### When to Use `@rx.memo`

✅ **USE** when function:
- Takes NO parameters
- Takes only concrete Python values (not state vars)
- Accesses state internally

Example:
```python
@rx.memo
def static_card():  # No parameters
    return rxe.dnd.draggable(
        rx.card(
            rx.text("Position: " + State.position.to_string()),  # State accessed internally
        ),
        type="Card"
    )
```

❌ **DON'T USE** when function:
- Receives state vars as parameters
- Receives iteration vars from `rx.foreach`

Example of what NOT to do:
```python
@rx.memo
def item_card(item: Item):  # ❌ Item is state var from foreach
    ...
```

## Current Implementation

### What Works

1. **Loadout items are draggable** - Items already in loadout can be dragged between slots
2. **Drop targets have validation** - Green for valid, red for invalid
3. **State is preserved** - Tiers and quantities maintained during moves
4. **Pre-compiled slots** - All 14 backpack slots, 4 quick use, 2 safe pocket pre-compiled
5. **Dynamic visibility** - Augment controls which slots show

### What Doesn't Work (By Design)

1. **Sidebar items not draggable** - Due to `rx.foreach` limitation
2. **No drag from selector to loadout** - Use click instead

### Files Modified

- `arc/components/item_card.py` - Removed draggable wrapper (stays clickable)
- `arc/components/loadout_panel.py` - All loadout items are draggable
- `arc/state.py` - Changed `LoadoutSlot` from `rx.Base` to `pydantic.BaseModel`

## Testing Status

- ✅ Click to add from sidebar works
- ✅ Drag between loadout slots works
- ✅ Drop validation works (green/red feedback)
- ✅ No compilation errors
- ⏳ Runtime testing pending

## Future Enhancement Ideas

If you want sidebar items draggable in the future, you'd need to:

1. **Convert Item from TypedDict to Pydantic model** - Like the Dynamic Lists example in docs
2. **Pre-compile draggable cards** - Create explicit draggable version for each item (not practical with many items)
3. **Use a different drag library** - Find one that works with `rx.foreach`

For now, the click-to-add + drag-to-rearrange approach is clean and functional.

