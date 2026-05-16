from models.items import Item, Potion, Weapon, Armor, Buff


class Inventory:
    MAX_SIZE = 20

    RARITY_SYMBOL = {
        "common": "○",
        "uncommon": "◈",
        "rare": "◆",
        "legendary": "★",
    }

    def __init__(self):
        self._items: list[tuple[Item, int]] = []
        self._discovered_ids: set[int] = set()

    @property
    def items(self) -> list[tuple[Item, int]]:
        return self._items

    @property
    def is_full(self) -> bool:
        return len(self._items) >= self.MAX_SIZE

    @property
    def discovered_ids(self) -> set[int]:
        return self._discovered_ids

    def add_item(self, item: Item, quantity: int = 1) -> str:
        self._discovered_ids.add(item.item_id)
        for i, (existing, qty) in enumerate(self._items):
            if existing.item_id == item.item_id:
                self._items[i] = (existing, qty + quantity)
                return f"Added {quantity}x {item.name} (now x{qty + quantity})."
        if self.is_full:
            return f"Inventory full! Could not add {item.name}."
        self._items.append((item, quantity))
        return f"Picked up {item.name}!"

    def remove_item(self, item_id: int, quantity: int = 1) -> bool:
        for i, (item, qty) in enumerate(self._items):
            if item.item_id == item_id:
                if qty > quantity:
                    self._items[i] = (item, qty - quantity)
                else:
                    self._items.pop(i)
                return True
        return False

    def get_item(self, item_id: int) -> Item | None:
        for item, _ in self._items:
            if item.item_id == item_id:
                return item
        return None

    def get_consumables(self) -> list[tuple[Item, int]]:
        return [(item, qty) for item, qty in self._items
                if isinstance(item, (Potion, Buff))]

    def get_equipment(self) -> list[tuple[Item, int]]:
        return [(item, qty) for item, qty in self._items
                if isinstance(item, (Weapon, Armor))]

    def use_item(self, index: int, character) -> str:
        if index < 0 or index >= len(self._items):
            return "Invalid item selection."
        item, _ = self._items[index]
        msg = item.use(character)
        if isinstance(item, (Potion, Buff)):
            self.remove_item(item.item_id, 1)
        return msg

    def display(self) -> str:
        if not self._items:
            return "  [Empty]"
        lines = []
        for i, (item, qty) in enumerate(self._items):
            sym = self.RARITY_SYMBOL.get(item.rarity, "○")
            tag = f"[{item.item_type[0].upper()}]"
            lines.append(f"  [{i + 1}] {sym} {tag} {item.name} x{qty}  —  {item.description}")
        return "\n".join(lines)

    def to_list(self) -> list[dict]:
        return [{"item_id": item.item_id, "quantity": qty}
                for item, qty in self._items]

    def __len__(self) -> int:
        return len(self._items)
