import reflex as rx
from arc.state import CalculatorState


def tier_selector(item_id: str) -> rx.Component:
    """A component to select the tier for a weapon."""
    tiers = ["I", "II", "III", "IV"]
    selected_tier = CalculatorState.selected_weapon_tiers.get(item_id, 1)
    return rx.el.div(
        rx.foreach(
            tiers,
            lambda tier, index: rx.el.button(
                tier,
                on_click=lambda: CalculatorState.set_weapon_tier(
                    item_id, index + 1
                ),
                class_name=rx.cond(
                    selected_tier == index + 1,
                    "w-8 h-8 text-xs font-bold text-white bg-[#22BFFB] rounded-md",
                    "w-8 h-8 text-xs font-semibold text-white bg-[#5D605D] rounded-md hover:bg-[#3DEB58]",
                ),
                size="1",
            ),
        ),
        class_name="flex items-center gap-1.5",
        on_click=rx.stop_propagation,
    )