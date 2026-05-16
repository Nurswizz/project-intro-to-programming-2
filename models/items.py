from abc import ABC, abstractmethod


class Item(ABC):
    def __init__(self, item_id: int, name: str, description: str,
                 rarity: str, price: int):
        self._item_id = item_id
        self._name = name
        self._description = description
        self._rarity = rarity
        self._price = price

    @property
    def item_id(self) -> int:
        return self._item_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def rarity(self) -> str:
        return self._rarity

    @property
    def price(self) -> int:
        return self._price

    @property
    @abstractmethod
    def item_type(self) -> str:
        pass

    @property
    @abstractmethod
    def effect_value(self) -> int:
        pass

    @abstractmethod
    def use(self, character) -> str:
        pass

    def __str__(self) -> str:
        return f"{self._name} [{self._rarity}] — {self._description}"


class Potion(Item):
    def __init__(self, item_id: int, name: str, heal_amount: int,
                 description: str, rarity: str = "common", price: int = 20):
        super().__init__(item_id, name, description, rarity, price)
        self._heal_amount = heal_amount

    @property
    def item_type(self) -> str:
        return "potion"

    @property
    def effect_value(self) -> int:
        return self._heal_amount

    def use(self, character) -> str:
        if self._heal_amount == 0:
            character.cure_status()
            return f"Used {self._name}! All status effects cured."
        healed = character.heal(self._heal_amount)
        return (f"Used {self._name}! Restored {healed} HP. "
                f"(HP: {character.hp}/{character.max_hp})")


class Weapon(Item):
    def __init__(self, item_id: int, name: str, attack_bonus: int,
                 description: str, rarity: str = "common", price: int = 30):
        super().__init__(item_id, name, description, rarity, price)
        self._attack_bonus = attack_bonus

    @property
    def item_type(self) -> str:
        return "weapon"

    @property
    def effect_value(self) -> int:
        return self._attack_bonus

    def use(self, character) -> str:
        if hasattr(character, "equip_weapon"):
            return character.equip_weapon(self)
        return f"Cannot equip {self._name}."


class Armor(Item):
    def __init__(self, item_id: int, name: str, defense_bonus: int,
                 description: str, rarity: str = "common", price: int = 35):
        super().__init__(item_id, name, description, rarity, price)
        self._defense_bonus = defense_bonus

    @property
    def item_type(self) -> str:
        return "armor"

    @property
    def effect_value(self) -> int:
        return self._defense_bonus

    def use(self, character) -> str:
        if hasattr(character, "equip_armor"):
            return character.equip_armor(self)
        return f"Cannot equip {self._name}."


class Buff(Item):
    def __init__(self, item_id: int, name: str, buff_type: str, duration: int,
                 description: str, rarity: str = "uncommon", price: int = 60):
        super().__init__(item_id, name, description, rarity, price)
        self._buff_type = buff_type
        self._duration = duration

    @property
    def item_type(self) -> str:
        return "buff"

    @property
    def effect_value(self) -> int:
        return self._duration

    @property
    def buff_type(self) -> str:
        return self._buff_type

    def use(self, character) -> str:
        character.apply_status(self._buff_type, self._duration)
        return f"Used {self._name}! {self._buff_type} active for {self._duration} turns."


class ItemFactory:
    @staticmethod
    def create(data: dict) -> Item:
        item_id = int(data["id"])
        name = data["name"]
        item_type = data["type"]
        effect_value = int(data["effect_value"])
        description = data["description"]
        rarity = data.get("rarity", "common")
        price = int(data.get("price", 0))

        if item_type == "potion":
            return Potion(item_id, name, effect_value, description, rarity, price)
        if item_type == "weapon":
            return Weapon(item_id, name, effect_value, description, rarity, price)
        if item_type == "armor":
            return Armor(item_id, name, effect_value, description, rarity, price)
        if item_type == "buff":
            return Buff(item_id, name, "speed_boost", effect_value, description, rarity, price)
        return Potion(item_id, name, effect_value, description, rarity, price)
