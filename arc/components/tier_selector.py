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
                    "w-5 h-5 sm:w-6 sm:h-6 md:w-6 md:h-6 text-[9px] sm:text-[10px] font-bold text-white bg-[#22BFFB] rounded-md",
                    "w-5 h-5 sm:w-6 sm:h-6 md:w-6 md:h-6 text-[9px] sm:text-[10px] font-semibold text-white bg-[#5D605D] rounded-md hover:bg-[#3DEB58]",
                ),
                size="1",
            ),
        ),
        class_name="flex items-center gap-0.5 sm:gap-1",
        on_click=rx.stop_propagation,
    )