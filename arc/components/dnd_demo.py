import reflex as rx
import reflex_enterprise as rxe
from typing import Any


class DndDemoState(rx.State):
    """State for the drag-and-drop demo."""
    
    card_position: int = 0
    num_drop_zones: int = 3
    
    @rx.event
    def set_card_position(self, position: int):
        """Moves the card to a new position based on drop target."""
        self.card_position = position
    
    @rx.event
    def set_num_drop_zones(self, value: list[float]):
        """Sets the number of drop zones."""
        if value and len(value) > 0:
            new_num = int(value[0])
            self.num_drop_zones = new_num
            # If card position is now out of bounds, move it to zone 0
            if self.card_position >= new_num:
                self.card_position = 0


@rx.memo
def movable_card():
    """A draggable card component."""
    return rxe.dnd.draggable(
        rx.card(
            rx.text("Movable Card", weight="bold"),
            rx.text("Position: " + DndDemoState.card_position.to_string()),
            bg="sky.500",
            color="white",
            p=4,
            width="180px",
            height="120px",
        ),
        type="MovableCard",
        border="2px solid sky",
    )


def drop_zone(position: int):
    """Create a drop zone for a specific position."""
    params = rxe.dnd.DropTarget.collected_params
    return rxe.dnd.drop_target(
        rx.cond(
            DndDemoState.card_position == position,
            movable_card(),
            rx.box(
                f"Drop Zone {position + 1}", 
                color="black", 
                font_weight="bold"
            ),
        ),
        width="100%",
        height="150px",
        border="2px solid",
        border_color=rx.cond(params.is_over, "green", "gray.300"),
        bg=rx.cond(params.is_over, "green", "white"),
        accept=["MovableCard"],
        on_drop=lambda _: DndDemoState.set_card_position(position),
        display="flex",
        align_items="center",
        justify_content="center",
    )


def dnd_demo_panel() -> rx.Component:
    """The drag-and-drop demo panel."""
    return rxe.dnd.provider(
        rx.vstack(
            rx.heading(
                "Drag & Drop Demo",
                size="7",
                color="black",
            ),
            rx.text(
                "Drag the card between positions",
                color="black",
                size="2",
            ),
            rx.vstack(
                rx.text(
                    "Number of Drop Zones:",
                    font_weight="bold",
                    color="black",
                    size="2",
                ),
                rx.slider(
                    default_value=[3],
                    min=1,
                    max=8,
                    step=1,
                    on_value_commit=DndDemoState.set_num_drop_zones,
                    width="100%",
                ),
                rx.text(
                    f"Current: {DndDemoState.num_drop_zones}",
                    color="black",
                    size="1",
                ),
                spacing="2",
                width="100%",
            ),
            rx.cond(
                DndDemoState.num_drop_zones >= 1,
                rx.vstack(
                    drop_zone(0),
                    rx.cond(
                        DndDemoState.num_drop_zones >= 2,
                        drop_zone(1),
                    ),
                    rx.cond(
                        DndDemoState.num_drop_zones >= 3,
                        drop_zone(2),
                    ),
                    rx.cond(
                        DndDemoState.num_drop_zones >= 4,
                        drop_zone(3),
                    ),
                    rx.cond(
                        DndDemoState.num_drop_zones >= 5,
                        drop_zone(4),
                    ),
                    rx.cond(
                        DndDemoState.num_drop_zones >= 6,
                        drop_zone(5),
                    ),
                    rx.cond(
                        DndDemoState.num_drop_zones >= 7,
                        drop_zone(6),
                    ),
                    rx.cond(
                        DndDemoState.num_drop_zones >= 8,
                        drop_zone(7),
                    ),
                    spacing="4",
                    width="100%",
                ),
            ),
            spacing="4",
            padding="6",
            width="100%",
            height="100%",
            overflow_y="auto",
        ),
    )

