# Reflex Enterprise Drag-and-Drop: Dynamic Slots Solution

## Summary

Reflex Enterprise's drag-and-drop components work correctly with dynamic slot counts, but require **pre-compiling drop zones with concrete position values** rather than using `rx.foreach` with reactive loop variables. This is due to how Reflex compiles event handlers at build time.

## The Problem: `rx.foreach` with Event Handlers

### What Doesn't Work

```python
# ❌ This pattern fails
rx.foreach(
    rx.Var.range(num_slots),
    lambda position_var: drop_zone_with_handler(position_var)
)

def drop_zone_with_handler(position_var):
    return rxe.dnd.drop_target(
        ...,
        on_drop=lambda item: State.handle_drop(position_var),  # Problem here
    )
```

### Why It Fails

1. **Compile-time vs Runtime Mismatch**
   - Event handlers are compiled to JavaScript at **build time**
   - `position_var` from `rx.foreach` is a reactive `Var[int]` that only has a value at **runtime**
   - The compiler can't properly capture the runtime variable in a compile-time event handler

2. **Variable Reference Errors**
   - Results in JavaScript errors like: `ReferenceError: i_rx_state_ is not defined`
   - The loop variable isn't properly bound in the compiled JavaScript closure

3. **Variable Name Collisions**
   - When multiple drop zones are created, they may try to use the same variable names
   - Results in: `Identifier 'dropTargetCollectedParams' has already been declared`

## The Solution: Pre-compile with Concrete Values

### What Works

```python
# ✅ This pattern works
def drop_zone(position: int):  # position is a concrete Python int
    params = rxe.dnd.DropTarget.collected_params
    return rxe.dnd.drop_target(
        rx.cond(
            State.item_position == position,
            draggable_item(),
            empty_slot_display(),
        ),
        accept=["ItemType"],
        on_drop=lambda _: State.move_to_position(position),  # Captures concrete int
        droppable_id=f"slot-{position}",
        index=position,
    )

# Show/hide zones based on dynamic state
rx.cond(
    State.num_slots >= 1,
    rx.vstack(
        drop_zone(0),
        rx.cond(State.num_slots >= 2, drop_zone(1)),
        rx.cond(State.num_slots >= 3, drop_zone(2)),
        # ... up to max slots
    ),
)
```

### Why It Works

1. **Concrete Values at Compile Time**
   - Each `drop_zone(0)`, `drop_zone(1)`, etc. is called with a real Python `int`
   - The lambda captures this concrete value: `lambda _: State.move_to_position(0)`
   - Compiles to clean JavaScript: `() => move_to_position(0)`

2. **Runtime Visibility Control**
   - All drop zones are compiled into JavaScript upfront
   - `rx.cond` statements control which ones are rendered at runtime
   - React simply shows/hides components based on state

3. **No Variable Collisions**
   - Each drop zone is a separate compiled component
   - Each has unique variable names in the generated JavaScript

## Application to Arc Raiders Loadout System

This solution is **ideal** for the loadout calculator because:

### Current Architecture Match

```python
# Backpack has a maximum of 14 slots, but augment determines actual count
max_backpack_slots: int = 14  # Fixed maximum
current_slots = augment.backpack_slots  # Dynamic based on augment

# Pre-compile all possible slots
def backpack_slot(index: int):
    return rxe.dnd.drop_target(
        rx.cond(
            index < State.loadout_backpack.length(),
            show_item(State.loadout_backpack[index]),
            empty_slot(),
        ),
        accept=["Weapon", "Healing", "Trap"],
        on_drop=lambda item: State.drop_in_backpack(item, index),
        droppable_id=f"backpack-{index}",
        index=index,
    )

# Show only the slots allowed by current augment
rx.cond(
    State.max_backpack_slots >= 1,
    rx.grid(
        backpack_slot(0),
        rx.cond(State.max_backpack_slots >= 2, backpack_slot(1)),
        rx.cond(State.max_backpack_slots >= 3, backpack_slot(2)),
        # ... up to 14
        columns="4",
    ),
)
```

### Benefits

1. **Fixed Maximum**: You already know the max slots (14 backpack, 4 quick use, 2 safe pocket)
2. **Dynamic Display**: Augment changes which slots are visible, not which exist
3. **Clean Event Handlers**: Each slot's drop handler knows its exact index
4. **No Performance Penalty**: Conditional rendering is cheap; React handles it efficiently

## Key Takeaway

The limitation isn't with Reflex Enterprise DnD or dynamic slot counts - it's with the pattern of using `rx.foreach` for components that need event handlers with loop-variable-dependent behavior. The pre-compilation pattern is both the solution **and** the more semantically correct approach for a system with fixed maximum slots and dynamic visibility.

## Implementation Checklist

- [x] Install `reflex-enterprise` package
- [x] Import with `import reflex_enterprise as rxe` (not `from`)
- [x] Use `rxe.App()` instead of `rx.App()`
- [x] Wrap app in `rxe.dnd.provider()`
- [x] Define draggable items with `rxe.dnd.draggable()`
- [x] Create drop zone functions with concrete position parameters
- [x] Use `rx.cond()` to show/hide zones based on dynamic state
- [x] Use lambda event handlers that capture concrete position values
- [x] Add `@rx.memo` decorator to draggable components

## Working Demo

See `arc/components/dnd_demo.py` for a complete working example with:
- Variable number of drop zones (1-8)
- Draggable card that moves between zones
- Slider to dynamically change available slots
- Visual feedback on hover (using `collected_params`)

The demo proves that dynamic slot counts work perfectly with Reflex Enterprise DnD when using the pre-compilation pattern.
