import reflex as rx
from typing import TypedDict, Literal, cast

Rarity = Literal["Common", "Uncommon", "Rare", "Epic", "Legendary"]
ResourceType = Literal["basic", "refined"]


class ResourceCost(TypedDict):
    resource: str
    quantity: int


class Resource(TypedDict):
    id: str
    name: str
    category: Literal["resource"]
    resource_type: ResourceType
    image: str | None
    resources: list[ResourceCost]
    rarity: Rarity


class ResourceDisplay(TypedDict):
    id: str
    name: str
    quantity: int
    resource_type: ResourceType
    rarity: Rarity
    image: str | None


class Item(TypedDict):
    id: str
    name: str
    category: Literal["Weapon", "Augment", "Shield", "Healing", "Trap", "Gear", "Gadget", "Tool"]
    icon: str
    image: str | None
    resources: list[ResourceCost]
    tier_resources: dict[int, list[ResourceCost]]
    rarity: Rarity
    backpack_slots: int | None
    safe_pocket_slots: int | None
    quick_use_slots: int | None
    max_shield: str | None
    stack_size: int


class LoadoutItem(TypedDict):
    item_id: str
    quantity: int
    tier: int | None


from arc.items_data import ITEMS
from arc.resource_data import RESOURCES, RESOURCE_BY_ID


class CalculatorState(rx.State):
    """Manages the state for the resource calculator."""

    all_items: list[Item] = ITEMS
    all_resources: list[Resource] = RESOURCES
    active_category: str = "All"
    search_query: str = ""
    selected_weapon_tiers: dict[str, int] = {}
    decomposed_resources: set[str] = set()
    
    loadout_augment: str | None = None
    loadout_shield: str | None = None
    loadout_weapon_1: dict[str, int | str | None] | None = None
    loadout_weapon_2: dict[str, int | str | None] | None = None
    loadout_backpack: list[dict[str, int | str | None]] = []
    loadout_quick_use: list[dict[str, int | str | None]] = []
    loadout_safe_pocket: list[dict[str, int | str | None]] = []
    
    resource_icons: dict[str, str] = {
        "Scrap Metal": "gem",
        "Polymer": "box",
        "Electronics": "cpu",
        "Chemicals": "flask-conical",
    }
    rarity_colors: dict[str, str] = {
        "Common": "text-gray-500",
        "Uncommon": "text-green-500",
        "Rare": "text-blue-500",
        "Epic": "text-pink-500",
        "Legendary": "text-yellow-500",
    }

    @rx.event
    def set_search_query(self, query: str):
        """Sets the search query for filtering items."""
        self.search_query = query

    @rx.event
    def select_category(self, category: str):
        """Sets the active category for filtering items."""
        self.active_category = category

    @rx.event
    def set_weapon_tier(self, item_id: str, tier: int):
        """Sets the tier for a specific weapon."""
        self.selected_weapon_tiers[item_id] = tier
    
    @rx.event
    def set_loadout_weapon_tier(self, slot: str, tier: int, index: int | None = None):
        """Sets the tier for a weapon in the loadout."""
        if slot == "weapon_1" and self.loadout_weapon_1:
            self.loadout_weapon_1["tier"] = tier
        elif slot == "weapon_2" and self.loadout_weapon_2:
            self.loadout_weapon_2["tier"] = tier
        elif slot == "backpack" and index is not None and index < len(self.loadout_backpack):
            self.loadout_backpack[index]["tier"] = tier

    @rx.event
    def clear_selection(self):
        """Clears all loadout items."""
        self.loadout_augment = None
        self.loadout_shield = None
        self.loadout_weapon_1 = None
        self.loadout_weapon_2 = None
        self.loadout_backpack = []
        self.loadout_quick_use = []
        self.loadout_safe_pocket = []
        self.selected_weapon_tiers = {}

    @rx.event
    def toggle_decompose_resource(self, resource_id: str):
        """Toggles the decomposition of a single resource."""
        if resource_id in self.decomposed_resources:
            self.decomposed_resources.remove(resource_id)
        else:
            self.decomposed_resources.add(resource_id)

    @rx.event
    def decompose_all_resources(self):
        """Decomposes all refined resources in the current total."""
        for resource_id, _ in self.total_resources.items():
            resource = RESOURCE_BY_ID.get(resource_id)
            if resource and resource["resource_type"] == "refined":
                self.decomposed_resources.add(resource_id)

    @rx.event
    def reset_decomposition(self):
        """Resets all decomposed resources to their original state."""
        self.decomposed_resources = set()

    @rx.event
    def handle_escape(self):
        """Clears loadout and search query."""
        self.loadout_augment = None
        self.loadout_shield = None
        self.loadout_weapon_1 = None
        self.loadout_weapon_2 = None
        self.loadout_backpack = []
        self.loadout_quick_use = []
        self.loadout_safe_pocket = []
        self.selected_weapon_tiers = {}
        self.search_query = ""
        return rx.set_value("search-input", "")

    @rx.event
    def focus_search(self):
        """Focusses the search input field."""
        return rx.set_focus("search-input")

    @rx.event
    def handle_key_event(self, result: str = ""):
        """Handles the result of the keydown script."""
        if result == "focus_search":
            return CalculatorState.focus_search()
        if result == "handle_escape":
            return CalculatorState.handle_escape()
    
    @rx.event
    def auto_equip_item(self, item_id: str):
        """Automatically equips an item to the best available slot based on its category."""
        item = next((i for i in self.all_items if i["id"] == item_id), None)
        if not item:
            return
        
        category = item["category"]
        
        if category == "Augment":
            self.loadout_augment = item_id
        elif category == "Shield":
            self.loadout_shield = item_id
        elif category == "Weapon":
            tier = self.selected_weapon_tiers.get(item_id, 1)
            if not self.loadout_weapon_1:
                self.loadout_weapon_1 = {"item_id": item_id, "quantity": 1, "tier": tier}
            elif not self.loadout_weapon_2:
                self.loadout_weapon_2 = {"item_id": item_id, "quantity": 1, "tier": tier}
            elif len(self.loadout_backpack) < self.max_backpack_slots:
                self.loadout_backpack.append({"item_id": item_id, "quantity": 1, "tier": tier})
        elif category in ["Trap", "Healing"]:
            if len(self.loadout_quick_use) < self.max_quick_use_slots:
                self.loadout_quick_use.append({"item_id": item_id, "quantity": 1, "tier": None})
            elif len(self.loadout_safe_pocket) < self.max_safe_pocket_slots:
                self.loadout_safe_pocket.append({"item_id": item_id, "quantity": 1, "tier": None})
        else:
            if len(self.loadout_backpack) < self.max_backpack_slots:
                self.loadout_backpack.append({"item_id": item_id, "quantity": 1, "tier": None})
    
    @rx.event
    def equip_to_loadout(self, item_id: str, slot: str):
        """Equips an item to a specific loadout slot."""
        item = next((i for i in self.all_items if i["id"] == item_id), None)
        if not item:
            return
        
        if slot == "augment" and item["category"] == "Augment":
            self.loadout_augment = item_id
        elif slot == "shield" and item["category"] == "Shield":
            self.loadout_shield = item_id
        elif slot == "weapon_1" and item["category"] == "Weapon":
            tier = self.selected_weapon_tiers.get(item_id, 1)
            self.loadout_weapon_1 = {"item_id": item_id, "quantity": 1, "tier": tier}
        elif slot == "weapon_2" and item["category"] == "Weapon":
            tier = self.selected_weapon_tiers.get(item_id, 1)
            self.loadout_weapon_2 = {"item_id": item_id, "quantity": 1, "tier": tier}
        elif slot == "backpack":
            if len(self.loadout_backpack) < self.max_backpack_slots:
                tier = self.selected_weapon_tiers.get(item_id, 1) if item["category"] == "Weapon" else None
                self.loadout_backpack.append({"item_id": item_id, "quantity": 1, "tier": tier})
        elif slot == "quick_use" and item["category"] in ["Trap", "Healing"]:
            if len(self.loadout_quick_use) < self.max_quick_use_slots:
                self.loadout_quick_use.append({"item_id": item_id, "quantity": 1, "tier": None})
        elif slot == "safe_pocket" and item["category"] in ["Trap", "Healing"]:
            if len(self.loadout_safe_pocket) < self.max_safe_pocket_slots:
                self.loadout_safe_pocket.append({"item_id": item_id, "quantity": 1, "tier": None})
    
    @rx.event
    def unequip_from_loadout(self, slot: str, index: int | None = None):
        """Removes an item from a loadout slot."""
        if slot == "augment":
            self.loadout_augment = None
        elif slot == "shield":
            self.loadout_shield = None
        elif slot == "weapon_1":
            self.loadout_weapon_1 = None
        elif slot == "weapon_2":
            self.loadout_weapon_2 = None
        elif slot == "backpack" and index is not None and index < len(self.loadout_backpack):
            self.loadout_backpack.pop(index)
        elif slot == "quick_use" and index is not None and index < len(self.loadout_quick_use):
            self.loadout_quick_use.pop(index)
        elif slot == "safe_pocket" and index is not None and index < len(self.loadout_safe_pocket):
            self.loadout_safe_pocket.pop(index)
    
    @rx.event
    def increase_item_quantity(self, slot: str, index: int):
        """Increases the quantity of an item in a loadout slot."""
        loadout_list = None
        if slot == "backpack":
            loadout_list = self.loadout_backpack
        elif slot == "quick_use":
            loadout_list = self.loadout_quick_use
        elif slot == "safe_pocket":
            loadout_list = self.loadout_safe_pocket
        
        if loadout_list is not None and index < len(loadout_list):
            loadout_item = loadout_list[index]
            item = next((i for i in self.all_items if i["id"] == loadout_item["item_id"]), None)
            if item and loadout_item["quantity"] < item["stack_size"]:
                loadout_list[index] = {"item_id": loadout_item["item_id"], "quantity": loadout_item["quantity"] + 1}
    
    @rx.event
    def decrease_item_quantity(self, slot: str, index: int):
        """Decreases the quantity of an item in a loadout slot."""
        loadout_list = None
        if slot == "backpack":
            loadout_list = self.loadout_backpack
        elif slot == "quick_use":
            loadout_list = self.loadout_quick_use
        elif slot == "safe_pocket":
            loadout_list = self.loadout_safe_pocket
        
        if loadout_list is not None and index < len(loadout_list):
            loadout_item = loadout_list[index]
            if loadout_item["quantity"] > 1:
                loadout_list[index] = {"item_id": loadout_item["item_id"], "quantity": loadout_item["quantity"] - 1}

    @rx.var
    def loadout_augment_item(self) -> Item | None:
        """Returns the augment item object if equipped."""
        if self.loadout_augment:
            return next((i for i in self.all_items if i["id"] == self.loadout_augment), None)
        return None
    
    @rx.var
    def loadout_shield_item(self) -> Item | None:
        """Returns the shield item object if equipped."""
        if self.loadout_shield:
            return next((i for i in self.all_items if i["id"] == self.loadout_shield), None)
        return None
    
    @rx.var
    def loadout_weapon_1_item(self) -> Item | None:
        """Returns weapon 1 item object if equipped."""
        if self.loadout_weapon_1:
            return next((i for i in self.all_items if i["id"] == self.loadout_weapon_1["item_id"]), None)
        return None
    
    @rx.var
    def loadout_weapon_2_item(self) -> Item | None:
        """Returns weapon 2 item object if equipped."""
        if self.loadout_weapon_2:
            return next((i for i in self.all_items if i["id"] == self.loadout_weapon_2["item_id"]), None)
        return None
    
    @rx.var
    def loadout_backpack_items(self) -> list[Item]:
        """Returns list of item objects in backpack."""
        return [next((i for i in self.all_items if i["id"] == loadout_item["item_id"]), {"id": "", "name": "", "category": "Weapon", "icon": "", "image": None, "resources": [], "tier_resources": {}, "rarity": "Common", "backpack_slots": None, "safe_pocket_slots": None, "quick_use_slots": None, "max_shield": None, "stack_size": 1})
                for loadout_item in self.loadout_backpack]
    
    @rx.var
    def loadout_quick_use_items(self) -> list[Item]:
        """Returns list of item objects in quick use."""
        return [next((i for i in self.all_items if i["id"] == loadout_item["item_id"]), {"id": "", "name": "", "category": "Weapon", "icon": "", "image": None, "resources": [], "tier_resources": {}, "rarity": "Common", "backpack_slots": None, "safe_pocket_slots": None, "quick_use_slots": None, "max_shield": None, "stack_size": 1})
                for loadout_item in self.loadout_quick_use]
    
    @rx.var
    def loadout_safe_pocket_items(self) -> list[Item]:
        """Returns list of item objects in safe pocket."""
        return [next((i for i in self.all_items if i["id"] == loadout_item["item_id"]), {"id": "", "name": "", "category": "Weapon", "icon": "", "image": None, "resources": [], "tier_resources": {}, "rarity": "Common", "backpack_slots": None, "safe_pocket_slots": None, "quick_use_slots": None, "max_shield": None, "stack_size": 1})
                for loadout_item in self.loadout_safe_pocket]

    @rx.var
    def max_backpack_slots(self) -> int:
        """Returns the max backpack slots based on equipped augment."""
        if self.loadout_augment:
            augment = next((i for i in self.all_items if i["id"] == self.loadout_augment), None)
            if augment and augment.get("backpack_slots"):
                return augment["backpack_slots"]
        return 14
    
    @rx.var
    def max_quick_use_slots(self) -> int:
        """Returns the max quick use slots based on equipped augment."""
        if self.loadout_augment:
            augment = next((i for i in self.all_items if i["id"] == self.loadout_augment), None)
            if augment and augment.get("quick_use_slots"):
                return augment["quick_use_slots"]
        return 4
    
    @rx.var
    def max_safe_pocket_slots(self) -> int:
        """Returns the max safe pocket slots based on equipped augment."""
        if self.loadout_augment:
            augment = next((i for i in self.all_items if i["id"] == self.loadout_augment), None)
            if augment and augment.get("safe_pocket_slots"):
                return augment["safe_pocket_slots"]
        return 0
    
    @staticmethod
    def get_resource_name(resource_id: str) -> str:
        """Returns the resource name from the resource ID."""
        resource = RESOURCE_BY_ID.get(resource_id)
        return resource["name"] if resource else resource_id
    
    def get_weapon_tier_resources(self, item_id: str, tier: int) -> list:
        """Returns the resources for a weapon at a specific tier."""
        item = next((i for i in self.all_items if i["id"] == item_id), None)
        if item and item["category"] == "Weapon":
            return item["tier_resources"].get(tier, [])
        return []

    @rx.var
    def filtered_items(self) -> list[Item]:
        """Returns a list of items filtered by category and search query."""
        items = self.all_items
        if self.active_category != "All":
            items = [item for item in items if item["category"] == self.active_category]
        if self.search_query.strip():
            query = self.search_query.lower().strip()
            items = [item for item in items if query in item["name"].lower()]
        return items

    @rx.var
    def total_resources(self) -> dict[str, int]:
        """Calculates the total resources required for the selected items and loadout items with quantities."""
        totals: dict[str, int] = {}
        
        # Helper function to decompose resources (not a method to avoid recursion tracking issues)
        def add_resource(resource_id: str, quantity: int) -> None:
            resource = RESOURCE_BY_ID.get(resource_id)
            if not resource:
                return
            
            # If this resource should be decomposed and it's refined, decompose it
            if resource_id in self.decomposed_resources and resource["resource_type"] == "refined":
                for component in resource["resources"]:
                    component_id = component["resource"]
                    component_quantity = component["quantity"] * quantity
                    # Recursively decompose
                    add_resource(component_id, component_quantity)
            else:
                # Don't decompose, just add to totals
                totals[resource_id] = totals.get(resource_id, 0) + quantity
        
        # Process loadout items (augment, shield, weapons)
        if self.loadout_augment:
            item = next((i for i in self.all_items if i["id"] == self.loadout_augment), None)
            if item:
                for cost in item["resources"]:
                    add_resource(cost["resource"], cost["quantity"])
        
        if self.loadout_shield:
            item = next((i for i in self.all_items if i["id"] == self.loadout_shield), None)
            if item:
                for cost in item["resources"]:
                    add_resource(cost["resource"], cost["quantity"])
        
        if self.loadout_weapon_1:
            item = next((i for i in self.all_items if i["id"] == self.loadout_weapon_1["item_id"]), None)
            if item:
                tier = self.loadout_weapon_1["tier"] or 1
                for t in range(1, tier + 1):
                    tier_costs = item["tier_resources"].get(t, [])
                    for cost in tier_costs:
                        add_resource(cost["resource"], cost["quantity"])
        
        if self.loadout_weapon_2:
            item = next((i for i in self.all_items if i["id"] == self.loadout_weapon_2["item_id"]), None)
            if item:
                tier = self.loadout_weapon_2["tier"] or 1
                for t in range(1, tier + 1):
                    tier_costs = item["tier_resources"].get(t, [])
                    for cost in tier_costs:
                        add_resource(cost["resource"], cost["quantity"])
        
        # Process loadout items with quantities (backpack, quick_use, safe_pocket)
        for loadout_item in self.loadout_backpack:
            item = next((i for i in self.all_items if i["id"] == loadout_item["item_id"]), None)
            if item:
                item_quantity = loadout_item["quantity"]
                if item["category"] == "Weapon":
                    tier = loadout_item.get("tier") or 1
                    for t in range(1, tier + 1):
                        tier_costs = item["tier_resources"].get(t, [])
                        for cost in tier_costs:
                            add_resource(cost["resource"], cost["quantity"] * item_quantity)
                else:
                    for cost in item["resources"]:
                        add_resource(cost["resource"], cost["quantity"] * item_quantity)
        
        for loadout_item in self.loadout_quick_use:
            item = next((i for i in self.all_items if i["id"] == loadout_item["item_id"]), None)
            if item:
                item_quantity = loadout_item["quantity"]
                for cost in item["resources"]:
                    add_resource(cost["resource"], cost["quantity"] * item_quantity)
        
        for loadout_item in self.loadout_safe_pocket:
            item = next((i for i in self.all_items if i["id"] == loadout_item["item_id"]), None)
            if item:
                item_quantity = loadout_item["quantity"]
                for cost in item["resources"]:
                    add_resource(cost["resource"], cost["quantity"] * item_quantity)
        
        return totals

    @rx.var
    def sorted_total_resources(self) -> list[ResourceDisplay]:
        """Returns the total resources with full display information, sorted by rarity."""
        items: list[ResourceDisplay] = []
        for resource_id, quantity in self.total_resources.items():
            resource = RESOURCE_BY_ID.get(resource_id)
            if resource:
                items.append({
                    "id": resource_id,
                    "name": resource["name"],
                    "quantity": quantity,
                    "resource_type": resource["resource_type"],
                    "rarity": resource["rarity"],
                    "image": resource["image"],
                })
        # Define rarity order (highest rarity first)
        rarity_order = {"Legendary": 0, "Epic": 1, "Rare": 2, "Uncommon": 3, "Common": 4}
        # Sort by rarity (then by name for same rarity)
        return sorted(items, key=lambda x: (rarity_order.get(x["rarity"], 999), x["name"]))
    
    @rx.var
    def has_decomposed_resources(self) -> bool:
        """Returns whether any resources have been decomposed."""
        return len(self.decomposed_resources) > 0
    
    @rx.var
    def has_loadout_items(self) -> bool:
        """Returns whether any items are in the loadout."""
        return (
            self.loadout_augment is not None
            or self.loadout_shield is not None
            or self.loadout_weapon_1 is not None
            or self.loadout_weapon_2 is not None
            or len(self.loadout_backpack) > 0
            or len(self.loadout_quick_use) > 0
            or len(self.loadout_safe_pocket) > 0
        )
    
    @rx.var
    def decomposed_resources_display(self) -> list[ResourceDisplay]:
        """Returns a list of decomposed refined resources with their original quantities for display."""
        items: list[ResourceDisplay] = []
        
        # Calculate original resource requirements before decomposition from loadout
        original_totals: dict[str, int] = {}
        
        # Helper function to add resource costs
        def add_to_original(resource_id: str, quantity: int) -> None:
            original_totals[resource_id] = original_totals.get(resource_id, 0) + quantity
        
        # Process all loadout items
        if self.loadout_augment:
            item = next((i for i in self.all_items if i["id"] == self.loadout_augment), None)
            if item:
                for cost in item["resources"]:
                    add_to_original(cost["resource"], cost["quantity"])
        
        if self.loadout_shield:
            item = next((i for i in self.all_items if i["id"] == self.loadout_shield), None)
            if item:
                for cost in item["resources"]:
                    add_to_original(cost["resource"], cost["quantity"])
        
        if self.loadout_weapon_1:
            item = next((i for i in self.all_items if i["id"] == self.loadout_weapon_1["item_id"]), None)
            if item:
                tier = self.loadout_weapon_1["tier"] or 1
                for t in range(1, tier + 1):
                    for cost in item["tier_resources"].get(t, []):
                        add_to_original(cost["resource"], cost["quantity"])
        
        if self.loadout_weapon_2:
            item = next((i for i in self.all_items if i["id"] == self.loadout_weapon_2["item_id"]), None)
            if item:
                tier = self.loadout_weapon_2["tier"] or 1
                for t in range(1, tier + 1):
                    for cost in item["tier_resources"].get(t, []):
                        add_to_original(cost["resource"], cost["quantity"])
        
        for loadout_item in self.loadout_backpack:
            item = next((i for i in self.all_items if i["id"] == loadout_item["item_id"]), None)
            if item:
                if item["category"] == "Weapon":
                    tier = loadout_item.get("tier") or 1
                    for t in range(1, tier + 1):
                        for cost in item["tier_resources"].get(t, []):
                            add_to_original(cost["resource"], cost["quantity"] * loadout_item["quantity"])
                else:
                    for cost in item["resources"]:
                        add_to_original(cost["resource"], cost["quantity"] * loadout_item["quantity"])
        
        for loadout_item in self.loadout_quick_use:
            item = next((i for i in self.all_items if i["id"] == loadout_item["item_id"]), None)
            if item:
                for cost in item["resources"]:
                    add_to_original(cost["resource"], cost["quantity"] * loadout_item["quantity"])
        
        for loadout_item in self.loadout_safe_pocket:
            item = next((i for i in self.all_items if i["id"] == loadout_item["item_id"]), None)
            if item:
                for cost in item["resources"]:
                    add_to_original(cost["resource"], cost["quantity"] * loadout_item["quantity"])
        
        # Only include resources that are in decomposed_resources
        for resource_id in self.decomposed_resources:
            if resource_id in original_totals:
                resource = RESOURCE_BY_ID.get(resource_id)
                if resource:
                    items.append({
                        "id": resource_id,
                        "name": resource["name"],
                        "quantity": original_totals[resource_id],
                        "resource_type": resource["resource_type"],
                        "rarity": resource["rarity"],
                        "image": resource["image"],
                    })
        
        # Define rarity order (highest rarity first)
        rarity_order = {"Legendary": 0, "Epic": 1, "Rare": 2, "Uncommon": 3, "Common": 4}
        # Sort by rarity (then by name for same rarity)
        return sorted(items, key=lambda x: (rarity_order.get(x["rarity"], 999), x["name"]))