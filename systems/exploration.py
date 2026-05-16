import random
from dataclasses import dataclass
from models.character import Enemy
from models.items import Item


@dataclass
class Zone:
    name: str
    description: str
    min_level: int
    enemy_ids: list[int]
    event_weights: dict[str, int]


ZONES: list[Zone] = [
    Zone(
        name="Cursed Forest",
        description="A fog-laden forest hiding weak creatures.",
        min_level=1,
        enemy_ids=[1, 2],
        event_weights={"encounter": 55, "loot": 25, "empty": 15, "special": 5},
    ),
    Zone(
        name="Goblin Mines",
        description="Damp tunnels swarming with aggressive goblins.",
        min_level=2,
        enemy_ids=[1, 3],
        event_weights={"encounter": 60, "loot": 20, "empty": 15, "special": 5},
    ),
    Zone(
        name="Shadow Dungeon",
        description="A labyrinthine dungeon shrouded in eternal darkness.",
        min_level=3,
        enemy_ids=[3, 4, 5],
        event_weights={"encounter": 65, "loot": 20, "empty": 10, "special": 5},
    ),
    Zone(
        name="Dragon's Peak",
        description="A volcanic mountain range home to fearsome beasts.",
        min_level=5,
        enemy_ids=[5, 6],
        event_weights={"encounter": 70, "loot": 15, "empty": 10, "special": 5},
    ),
    Zone(
        name="Demon Realm",
        description="The scorched domain of the Demon Lord.",
        min_level=7,
        enemy_ids=[6, 7],
        event_weights={"encounter": 70, "loot": 15, "empty": 10, "special": 5},
    ),
    Zone(
        name="Shadow Monarch's Domain",
        description="The ultimate trial. Only the strongest survive.",
        min_level=10,
        enemy_ids=[7, 8],
        event_weights={"encounter": 75, "loot": 10, "empty": 10, "special": 5},
    ),
]

_RARITY_WEIGHTS = {"common": 50, "uncommon": 30, "rare": 15, "legendary": 5}

_SPECIAL_EVENTS = [
    {
        "type": "merchant",
        "text": "A hooded merchant steps from the shadows.",
        "reward": {"gold": (20, 50)},
    },
    {
        "type": "shrine",
        "text": "You discover an ancient healing shrine.",
        "reward": {"hp": "full"},
    },
    {
        "type": "treasure",
        "text": "A glittering treasure chest sits unguarded!",
        "reward": {"gold": (50, 150)},
    },
    {
        "type": "training",
        "text": "You stumble upon an abandoned training ground.",
        "reward": {"xp": (30, 80)},
    },
]


class ExplorationSystem:
    def __init__(self, all_enemies: list[Enemy], all_items: dict[int, Item]):
        self._enemies: dict[int, Enemy] = {e.enemy_id: e for e in all_enemies}
        self._items: dict[int, Item] = all_items

    def get_available_zones(self, player_level: int) -> list[Zone]:
        return [z for z in ZONES if z.min_level <= player_level]

    def choose_zone(self, player_level: int) -> Zone:
        available = self.get_available_zones(player_level)
        print("\n" + "═" * 50)
        print("  ★  EXPLORATION  —  Choose a Zone")
        print("═" * 50)
        for i, zone in enumerate(available):
            print(f"\n  [{i + 1}] {zone.name}  (Lv.{zone.min_level}+)")
            print(f"      {zone.description}")
        print()

        while True:
            raw = input("  > ").strip()
            try:
                idx = int(raw) - 1
                if 0 <= idx < len(available):
                    return available[idx]
                print("  Invalid choice.")
            except ValueError:
                print("  Enter a number.")

    def roll_event(self, zone: Zone) -> str:
        events = list(zone.event_weights.keys())
        weights = [zone.event_weights[e] for e in events]
        return random.choices(events, weights=weights, k=1)[0]

    def get_encounter_enemy(self, zone: Zone, player_level: int) -> Enemy:
        candidates = [self._enemies[eid] for eid in zone.enemy_ids
                      if eid in self._enemies]
        if not candidates:
            candidates = list(self._enemies.values())
        weights = [max(1, 10 - abs(e.level - player_level)) for e in candidates]
        return random.choices(candidates, weights=weights, k=1)[0].fresh_copy()

    def get_loot(self, _player_level: int) -> Item | None:
        if not self._items:
            return None
        items = list(self._items.values())
        weights = [_RARITY_WEIGHTS.get(it.rarity, 30) for it in items]
        return random.choices(items, weights=weights, k=1)[0]

    def loot_generator(self, player_level: int, count: int = 1):
        items = list(self._items.values())
        weights = [_RARITY_WEIGHTS.get(it.rarity, 30) for it in items]
        for _ in range(count):
            if items:
                yield random.choices(items, weights=weights, k=1)[0]

    def special_event(self, _player_level: int) -> dict:
        template = random.choice(_SPECIAL_EVENTS)
        event = {"type": template["type"], "text": template["text"], "reward": {}}
        for key, val in template["reward"].items():
            if isinstance(val, tuple):
                event["reward"][key] = random.randint(*val)
            else:
                event["reward"][key] = val
        return event
