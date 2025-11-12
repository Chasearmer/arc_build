from arc.state import Item
from arc.augments_data import AUGMENTS

WEAPONS: list[Item] = [
    {
    "id": "w_kettle",
    "name": "Kettle",
    "category": "Weapon",
    "icon": "locate-fixed",
    "image": "/items/w_kettle.webp",
    "resources": [],
    "tier_resources": {
        1: [
            {"resource": "r_metal_parts", "quantity": 6},
            {"resource": "r_rubber_parts", "quantity": 8},
        ],
        2: [
            {"resource": "r_metal_parts", "quantity": 8},
            {"resource": "r_plastic_parts", "quantity": 10},
        ],
        3: [
            {"resource": "r_metal_parts", "quantity": 10},
            {"resource": "r_simple_gun_parts", "quantity": 1},
        ],
        4: [
            {"resource": "r_mechanical_components", "quantity": 3},
            {"resource": "r_simple_gun_parts", "quantity": 1},
        ],
    },
    "rarity": "Common",
    "backpack_slots": None,
    "safe_pocket_slots": None,
    "quick_use_slots": None,
    "max_shield": None,
    "stack_size": 1,
},
{
    "id": "w_ferro",
    "name": "Ferro",
    "category": "Weapon",
    "icon": "locate-fixed",
    "image": "/items/w_ferro.webp",
    "resources": [],
    "tier_resources": {
        1: [
            {"resource": "r_metal_parts", "quantity": 5},
            {"resource": "r_rubber_parts", "quantity": 2},
        ],
        2: [
            {"resource": "r_metal_parts", "quantity": 7},
        ],
        3: [
            {"resource": "r_metal_parts", "quantity": 9},
            {"resource": "r_simple_gun_parts", "quantity": 1},
        ],
        4: [
            {"resource": "r_mechanical_components", "quantity": 1},
            {"resource": "r_simple_gun_parts", "quantity": 1},
        ],
    },
    "rarity": "Common",
    "backpack_slots": None,
    "safe_pocket_slots": None,
    "quick_use_slots": None,
    "max_shield": None,
    "stack_size": 1,
},
{
    "id": "w_stitcher",
    "name": "Stitcher",
    "category": "Weapon",
    "icon": "locate-fixed",
    "image": "/items/w_stitcher.webp",
    "resources": [],
    "tier_resources": {
        1: [
            {"resource": "r_metal_parts", "quantity": 8},
            {"resource": "r_rubber_parts", "quantity": 4},
        ],
        2: [
            {"resource": "r_metal_parts", "quantity": 8},
            {"resource": "r_rubber_parts", "quantity": 12},
        ],
        3: [
            {"resource": "r_metal_parts", "quantity": 10},
            {"resource": "r_simple_gun_parts", "quantity": 1},
        ],
        4: [
            {"resource": "r_mechanical_components", "quantity": 3},
            {"resource": "r_simple_gun_parts", "quantity": 1},
        ],
    },
    "rarity": "Common",
    "backpack_slots": None,
    "safe_pocket_slots": None,
    "quick_use_slots": None,
    "max_shield": None,
    "stack_size": 1,
},
{
    "id": "w_rattler",
    "name": "Rattler",
    "category": "Weapon",
    "icon": "locate-fixed",
    "image": "/items/w_rattler.webp",
    "resources": [],
    "tier_resources": {
        1: [
            {"resource": "r_metal_parts", "quantity": 10},
            {"resource": "r_rubber_parts", "quantity": 5},
        ],
        2: [
            {"resource": "r_metal_parts", "quantity": 8},
            {"resource": "r_rubber_parts", "quantity": 8},
        ],
        3: [
            {"resource": "r_metal_parts", "quantity": 6},
            {"resource": "r_magnet", "quantity": 2},
        ],
        4: [
            {"resource": "r_mechanical_components", "quantity": 3},
            {"resource": "r_simple_gun_parts", "quantity": 1},
        ],
    },
    "rarity": "Common",
    "backpack_slots": None,
    "safe_pocket_slots": None,
    "quick_use_slots": None,
    "max_shield": None,
    "stack_size": 1,
},
{
    "id": "w_hairpin",
    "name": "Hairpin",
    "category": "Weapon",
    "icon": "locate-fixed",
    "image": "/items/w_hairpin.webp",
    "resources": [],
    "tier_resources": {
        1: [
            {"resource": "r_metal_parts", "quantity": 2},
            {"resource": "r_plastic_parts", "quantity": 5},
        ],
        2: [
            {"resource": "r_metal_parts", "quantity": 8},
        ],
        3: [
            {"resource": "r_metal_parts", "quantity": 6},
            {"resource": "r_duct_tape", "quantity": 2},
        ],
        4: [
            {"resource": "r_metal_parts", "quantity": 10},
            {"resource": "r_simple_gun_parts", "quantity": 1},
        ],
    },
    "rarity": "Common",
    "backpack_slots": None,
    "safe_pocket_slots": None,
    "quick_use_slots": None,
    "max_shield": None,
    "stack_size": 1,
},
{
    "id": "w_anvil",
    "name": "Anvil",
    "category": "Weapon",
    "icon": "locate-fixed",
    "image": "/items/w_anvil.webp",
    "resources": [],
    "tier_resources": {
        1: [
            {"resource": "r_mechanical_components", "quantity": 5},
            {"resource": "r_simple_gun_parts", "quantity": 6},
        ],
        2: [
            {"resource": "r_mechanical_components", "quantity": 3},
            {"resource": "r_simple_gun_parts", "quantity": 1},
        ],
        3: [
            {"resource": "r_mechanical_components", "quantity": 4},
            {"resource": "r_heavy_gun_parts", "quantity": 1},
        ],
        4: [
            {"resource": "r_mechanical_components", "quantity": 4},
            {"resource": "r_heavy_gun_parts", "quantity": 1},
        ],
    },
    "rarity": "Uncommon",
    "backpack_slots": None,
    "safe_pocket_slots": None,
    "quick_use_slots": None,
    "max_shield": None,
    "stack_size": 1,
},
{
    "id": "w_il_toro",
    "name": "Il Toro",
    "category": "Weapon",
    "icon": "locate-fixed",
    "image": "/items/w_il_toro.webp",
    "resources": [],
    "tier_resources": {
        1: [
            {"resource": "r_mechanical_components", "quantity": 5},
            {"resource": "r_simple_gun_parts", "quantity": 6},
        ],
        2: [
            {"resource": "r_mechanical_components", "quantity": 3},
            {"resource": "r_simple_gun_parts", "quantity": 1},
        ],
        3: [
            {"resource": "r_mechanical_components", "quantity": 4},
            {"resource": "r_heavy_gun_parts", "quantity": 1},
        ],
        4: [
            {"resource": "r_mechanical_components", "quantity": 4},
            {"resource": "r_heavy_gun_parts", "quantity": 1},
        ],
    },
    "rarity": "Uncommon",
    "backpack_slots": None,
    "safe_pocket_slots": None,
    "quick_use_slots": None,
    "max_shield": None,
    "stack_size": 1,
},
{
    "id": "w_arpeggio",
    "name": "Arpeggio",
    "category": "Weapon",
    "icon": "locate-fixed",
    "image": "/items/w_arpeggio.webp",
    "resources": [],
    "tier_resources": {
        1: [
            {"resource": "r_mechanical_components", "quantity": 6},
            {"resource": "r_simple_gun_parts", "quantity": 6},
        ],
        2: [
            {"resource": "r_mechanical_components", "quantity": 4},
            {"resource": "r_simple_gun_parts", "quantity": 1},
        ],
        3: [
            {"resource": "r_mechanical_components", "quantity": 5},
            {"resource": "r_medium_gun_parts", "quantity": 1},
        ],
        4: [
            {"resource": "r_mechanical_components", "quantity": 5},
            {"resource": "r_medium_gun_parts", "quantity": 1},
        ],
    },
    "rarity": "Uncommon",
    "backpack_slots": None,
    "safe_pocket_slots": None,
    "quick_use_slots": None,
    "max_shield": None,
    "stack_size": 1,
},
{
    "id": "w_burletta",
    "name": "Burletta",
    "category": "Weapon",
    "icon": "locate-fixed",
    "image": "/items/w_burletta.webp",
    "resources": [],
    "tier_resources": {
        1: [
            {"resource": "r_mechanical_components", "quantity": 3},
            {"resource": "r_simple_gun_parts", "quantity": 3},
        ],
        2: [
            {"resource": "r_mechanical_components", "quantity": 3},
            {"resource": "r_simple_gun_parts", "quantity": 1},
        ],
        3: [
            {"resource": "r_mechanical_components", "quantity": 3},
            {"resource": "r_simple_gun_parts", "quantity": 1},
        ],
        4: [
            {"resource": "r_mechanical_components", "quantity": 4},
            {"resource": "r_light_gun_parts", "quantity": 1},
        ],
    },
    "rarity": "Uncommon",
    "backpack_slots": None,
    "safe_pocket_slots": None,
    "quick_use_slots": None,
    "max_shield": None,
    "stack_size": 1,
},
{
    "id": "w_venator",
    "name": "Venator",
    "category": "Weapon",
    "icon": "locate-fixed",
    "image": "/items/w_venator.png",
    "resources": [],
    "tier_resources": {
        1: [
            {"resource": "r_advanced_mechanical_components", "quantity": 2},
            {"resource": "r_medium_gun_parts", "quantity": 3},
            {"resource": "r_magnet", "quantity": 5}
        ],
        2: [
            {"resource": "r_advanced_mechanical_components", "quantity": 1},
            {"resource": "r_medium_gun_parts", "quantity": 2}
        ],
        3: [
            {"resource": "r_advanced_mechanical_components", "quantity": 1},
            {"resource": "r_medium_gun_parts", "quantity": 2}
        ],
        4: [
            {"resource": "r_advanced_mechanical_components", "quantity": 2},
            {"resource": "r_medium_gun_parts", "quantity": 2}
        ]
    },
    "rarity": "Rare",
    "backpack_slots": None,
    "safe_pocket_slots": None,
    "quick_use_slots": None,
    "max_shield": None,
    "stack_size": 1,
},
{
    "id": "w_renegade",
    "name": "Renegade",
    "category": "Weapon",
    "icon": "locate-fixed",
    "image": "/items/w_renegade.webp",
    "resources": [],
    "tier_resources": {
        1: [
            {"resource": "r_advanced_mechanical_components", "quantity": 2},
            {"resource": "r_medium_gun_parts", "quantity": 3},
            {"resource": "r_oil", "quantity": 5}
        ],
        2: [
            {"resource": "r_advanced_mechanical_components", "quantity": 1},
            {"resource": "r_medium_gun_parts", "quantity": 2}
        ],
        3: [
            {"resource": "r_advanced_mechanical_components", "quantity": 1},
            {"resource": "r_medium_gun_parts", "quantity": 2}
        ],
        4: [
            {"resource": "r_advanced_mechanical_components", "quantity": 2},
            {"resource": "r_medium_gun_parts", "quantity": 2}
        ]
    },
    "rarity": "Rare",
    "backpack_slots": None,
    "safe_pocket_slots": None,
    "quick_use_slots": None,
    "max_shield": None,
    "stack_size": 1,
},
{
    "id": "w_torrente",
    "name": "Torrente",
    "category": "Weapon",
    "icon": "locate-fixed",
    "image": "/items/w_torrente.png",
    "resources": [],
    "tier_resources": {
        1: [
            {"resource": "r_advanced_mechanical_components", "quantity": 2},
            {"resource": "r_medium_gun_parts", "quantity": 3},
            {"resource": "r_steel_spring", "quantity": 6}
        ],
        2: [
            {"resource": "r_advanced_mechanical_components", "quantity": 1},
            {"resource": "r_medium_gun_parts", "quantity": 2}
        ],
        3: [
            {"resource": "r_advanced_mechanical_components", "quantity": 1},
            {"resource": "r_medium_gun_parts", "quantity": 2}
        ],
        4: [
            {"resource": "r_advanced_mechanical_components", "quantity": 2},
            {"resource": "r_medium_gun_parts", "quantity": 2}
        ]
    },
    "rarity": "Rare",
    "backpack_slots": None,
    "safe_pocket_slots": None,
    "quick_use_slots": None,
    "max_shield": None,
    "stack_size": 1,
},
{
    "id": "w_osprey",
    "name": "Osprey",
    "category": "Weapon",
    "icon": "locate-fixed",
    "image": "/items/w_osprey.webp",
    "resources": [],
    "tier_resources": {
        1: [
            {"resource": "r_advanced_mechanical_components", "quantity": 2},
            {"resource": "r_medium_gun_parts", "quantity": 3},
            {"resource": "r_wires", "quantity": 7}
        ],
        2: [
            {"resource": "r_advanced_mechanical_components", "quantity": 1},
            {"resource": "r_medium_gun_parts", "quantity": 2}
        ],
        3: [
            {"resource": "r_advanced_mechanical_components", "quantity": 1},
            {"resource": "r_medium_gun_parts", "quantity": 2}
        ],
        4: [
            {"resource": "r_advanced_mechanical_components", "quantity": 2},
            {"resource": "r_medium_gun_parts", "quantity": 2}
        ]
    },
    "rarity": "Rare",
    "backpack_slots": None,
    "safe_pocket_slots": None,
    "quick_use_slots": None,
    "max_shield": None,
    "stack_size": 1,
},
]

SHIELDS: list[Item] = [
    {
        "id": "s_light_shield",
        "name": "Light Shield",
        "category": "Shield",
        "icon": "shield-half",
        "image": "/items/s_light_shield.png",
        "resources": [
            {"resource": "r_arc_alloy", "quantity": 2},
            {"resource": "r_plastic_parts", "quantity": 4},
        ],
        "tier_resources": {},
        "rarity": "Uncommon",
        "backpack_slots": None,
        "safe_pocket_slots": None,
        "quick_use_slots": None,
        "max_shield": None,
        "stack_size": 1,
    },
]

HEALING: list[Item] = [
    {
        "id": "h_bandage",
        "name": "Bandage",
        "category": "Healing",
        "icon": "bandage",
        "image": "/items/h_bandage.png",
        "resources": [
            {"resource": "r_fabric", "quantity": 5},
        ],
        "tier_resources": {},
        "rarity": "Common",
        "backpack_slots": None,
        "safe_pocket_slots": None,
        "quick_use_slots": None,
        "max_shield": None,
        "stack_size": 5,
    },
]

TRAPS: list[Item] = [
    {
        "id": "t_jolt_mine",
        "name": "Jolt Mine",
        "category": "Trap",
        "icon": "battery-charging",
        "image": "/items/t_jolt_mine.png",
        "resources": [
            {"resource": "r_electrical_components", "quantity": 1},
            {"resource": "r_battery", "quantity": 1},
        ],
        "tier_resources": {},
        "rarity": "Rare",
        "backpack_slots": None,
        "safe_pocket_slots": None,
        "quick_use_slots": None,
        "max_shield": None,
        "stack_size": 3,
    },
]

ITEMS: list[Item] = AUGMENTS + WEAPONS + SHIELDS + HEALING + TRAPS

