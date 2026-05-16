from abc import ABC, abstractmethod


class Character(ABC):
    def __init__(self, name: str, hp: int, attack: int, defense: int, level: int = 1):
        self._name = name
        self._max_hp = hp
        self._hp = hp
        self._attack = attack
        self._defense = defense
        self._level = level
        self._status_effects: dict[str, int] = {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def hp(self) -> int:
        return self._hp

    @property
    def max_hp(self) -> int:
        return self._max_hp

    @property
    def attack(self) -> int:
        return self._attack

    @property
    def defense(self) -> int:
        return self._defense

    @property
    def level(self) -> int:
        return self._level

    @property
    def is_alive(self) -> bool:
        return self._hp > 0

    @property
    def status_effects(self) -> dict[str, int]:
        return self._status_effects

    def take_damage(self, damage: int) -> int:
        actual = max(1, damage - self._defense)
        self._hp = max(0, self._hp - actual)
        return actual

    def take_magic_damage(self, damage: int) -> int:
        actual = max(1, damage - self._defense // 2)
        self._hp = max(0, self._hp - actual)
        return actual

    def heal(self, amount: int) -> int:
        old_hp = self._hp
        self._hp = min(self._max_hp, self._hp + amount)
        return self._hp - old_hp

    def apply_status(self, effect: str, duration: int) -> None:
        self._status_effects[effect] = duration

    def cure_status(self, effect: str = None) -> None:
        if effect:
            self._status_effects.pop(effect, None)
        else:
            self._status_effects.clear()

    def is_stunned(self) -> bool:
        return self._status_effects.get("stun", 0) > 0

    def process_status_effects(self) -> list[str]:
        messages = []
        to_remove = []

        if "poison" in self._status_effects:
            dmg = max(3, self._max_hp // 10)
            self._hp = max(0, self._hp - dmg)
            messages.append(f"{self._name} takes {dmg} poison damage!")
            self._status_effects["poison"] -= 1
            if self._status_effects["poison"] <= 0:
                to_remove.append("poison")
                messages.append(f"{self._name} is no longer poisoned.")

        for effect in ("stun", "speed_boost"):
            if effect in self._status_effects:
                self._status_effects[effect] -= 1
                if self._status_effects[effect] <= 0:
                    to_remove.append(effect)
                    if effect == "stun":
                        messages.append(f"{self._name} recovers from stun.")
                    elif effect == "speed_boost":
                        messages.append(f"{self._name}'s speed boost fades.")

        for e in to_remove:
            del self._status_effects[e]

        return messages

    @abstractmethod
    def get_action(self) -> str:
        pass

    def __str__(self) -> str:
        return f"{self._name} (HP:{self._hp}/{self._max_hp} ATK:{self._attack} DEF:{self._defense})"


class Player(Character):
    _XP_BASE = 100
    _XP_SCALE = 1.5

    def __init__(self, name: str, hp: int = 100, attack: int = 10,
                 defense: int = 5, level: int = 1):
        super().__init__(name, hp, attack, defense, level)
        self._xp: int = 0
        self._xp_to_next: int = self._calc_xp_to_next(level)
        self._gold: int = 0
        self._kills: int = 0
        self._weapon_bonus: int = 0
        self._armor_bonus: int = 0
        self._equipped_weapon = None
        self._equipped_armor = None

    def _calc_xp_to_next(self, level: int) -> int:
        return int(self._XP_BASE * (level ** self._XP_SCALE))

    @property
    def xp(self) -> int:
        return self._xp

    @property
    def xp_to_next(self) -> int:
        return self._xp_to_next

    @property
    def gold(self) -> int:
        return self._gold

    @property
    def kills(self) -> int:
        return self._kills

    @property
    def equipped_weapon(self):
        return self._equipped_weapon

    @property
    def equipped_armor(self):
        return self._equipped_armor

    def add_gold(self, amount: int) -> None:
        self._gold += amount

    def spend_gold(self, amount: int) -> bool:
        if self._gold >= amount:
            self._gold -= amount
            return True
        return False

    def add_kill(self) -> None:
        self._kills += 1

    def gain_xp(self, amount: int) -> list[str]:
        messages = [f"Gained {amount} XP! ({self._xp + amount}/{self._xp_to_next})"]
        self._xp += amount

        while self._xp >= self._xp_to_next:
            self._xp -= self._xp_to_next
            self._level += 1
            self._xp_to_next = self._calc_xp_to_next(self._level)
            hp_gain, atk_gain, def_gain = 20, 3, 2
            self._max_hp += hp_gain
            self._attack += atk_gain
            self._defense += def_gain
            self._hp = self._max_hp
            messages += [
                "",
                "=" * 42,
                f"  ★  LEVEL UP!  You are now Level {self._level}!  ★",
                f"  HP  +{hp_gain} → {self._max_hp}  |  "
                f"ATK +{atk_gain} → {self._attack}  |  "
                f"DEF +{def_gain} → {self._defense}",
                f"  HP fully restored!",
                "=" * 42,
            ]

        return messages

    def equip_weapon(self, weapon) -> str:
        self._attack -= self._weapon_bonus
        self._weapon_bonus = weapon.effect_value
        self._attack += self._weapon_bonus
        self._equipped_weapon = weapon
        return f"Equipped {weapon.name}  (+{weapon.effect_value} ATK)"

    def equip_armor(self, armor) -> str:
        self._defense -= self._armor_bonus
        self._armor_bonus = armor.effect_value
        self._defense += self._armor_bonus
        self._equipped_armor = armor
        return f"Equipped {armor.name}  (+{armor.effect_value} DEF)"

    def to_dict(self) -> dict:
        return {
            "name": self._name,
            "hp": self._hp,
            "max_hp": self._max_hp,
            "attack": self._attack,
            "defense": self._defense,
            "level": self._level,
            "xp": self._xp,
            "xp_to_next": self._xp_to_next,
            "gold": self._gold,
            "kills": self._kills,
            "weapon_bonus": self._weapon_bonus,
            "armor_bonus": self._armor_bonus,
            "equipped_weapon_id": self._equipped_weapon.item_id if self._equipped_weapon else "none",
            "equipped_armor_id": self._equipped_armor.item_id if self._equipped_armor else "none",
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        p = cls(
            name=data["name"],
            hp=int(data["max_hp"]),
            attack=int(data["attack"]),
            defense=int(data["defense"]),
            level=int(data["level"]),
        )
        p._hp = int(data["hp"])
        p._xp = int(data["xp"])
        p._xp_to_next = int(data["xp_to_next"])
        p._gold = int(data["gold"])
        p._kills = int(data.get("kills", 0))
        p._weapon_bonus = int(data.get("weapon_bonus", 0))
        p._armor_bonus = int(data.get("armor_bonus", 0))
        return p

    def get_action(self) -> str:
        return "player"


class Enemy(Character):
    def __init__(self, enemy_id: int, name: str, hp: int, attack: int,
                 defense: int, xp_reward: int, gold_reward: int, level: int,
                 rank: str = "E", special_ability: str = "none"):
        super().__init__(name, hp, attack, defense, level)
        self._enemy_id = enemy_id
        self._xp_reward = xp_reward
        self._gold_reward = gold_reward
        self._rank = rank
        self._special_ability = special_ability

    @property
    def enemy_id(self) -> int:
        return self._enemy_id

    @property
    def xp_reward(self) -> int:
        return self._xp_reward

    @property
    def gold_reward(self) -> int:
        return self._gold_reward

    @property
    def rank(self) -> str:
        return self._rank

    @property
    def special_ability(self) -> str:
        return self._special_ability

    def get_action(self) -> str:
        import random
        if self._special_ability != "none" and random.random() < 0.30:
            return "special"
        return "attack"

    @classmethod
    def from_dict(cls, data: dict) -> "Enemy":
        return cls(
            enemy_id=int(data["id"]),
            name=data["name"],
            hp=int(data["hp"]),
            attack=int(data["attack"]),
            defense=int(data["defense"]),
            xp_reward=int(data["xp_reward"]),
            gold_reward=int(data["gold_reward"]),
            level=int(data["level"]),
            rank=data.get("rank", "E"),
            special_ability=data.get("special_ability", "none"),
        )

    def fresh_copy(self) -> "Enemy":
        return Enemy(
            enemy_id=self._enemy_id,
            name=self._name,
            hp=self._max_hp,
            attack=self._attack,
            defense=self._defense,
            xp_reward=self._xp_reward,
            gold_reward=self._gold_reward,
            level=self._level,
            rank=self._rank,
            special_ability=self._special_ability,
        )

    def __str__(self) -> str:
        return (f"[Rank {self._rank}] {self._name} "
                f"(HP:{self._hp}/{self._max_hp} ATK:{self._attack} DEF:{self._defense})")
