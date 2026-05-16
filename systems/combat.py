import random
from models.character import Player, Enemy
from systems.inventory import Inventory


class CombatResult:
    WIN = "win"
    LOSE = "lose"
    RAN = "ran"


class CombatSystem:
    def __init__(self, player: Player, enemy: Enemy, inventory: Inventory):
        self._player = player
        self._enemy = enemy
        self._inventory = inventory
        self._turn = 0

    def _hp_bar(self, current: int, maximum: int, width: int = 16) -> str:
        filled = int((current / max(1, maximum)) * width)
        return "█" * filled + "░" * (width - filled)

    def _print_status(self) -> None:
        p, e = self._player, self._enemy
        p_effects = ", ".join(f"{k}({v})" for k, v in p.status_effects.items()) or "—"
        e_effects = ", ".join(f"{k}({v})" for k, v in e.status_effects.items()) or "—"

        print(f"\n  {'─'*46}")
        print(f"  Enemy  : [Rank {e.rank}] {e.name}")
        print(f"  HP     : [{self._hp_bar(e.hp, e.max_hp)}] {e.hp}/{e.max_hp}")
        print(f"  Status : {e_effects}")
        print(f"  {'─'*46}")
        print(f"  You    : {p.name}  [Lv.{p.level}]")
        print(f"  HP     : [{self._hp_bar(p.hp, p.max_hp)}] {p.hp}/{p.max_hp}")
        print(f"  Status : {p_effects}")
        print(f"  {'─'*46}")

    def _player_turn(self) -> str:
        print("\n  Choose action:")
        print("  [1] Attack")
        print("  [2] Use Item")
        print("  [3] Run")

        while True:
            choice = input("\n  > ").strip()
            if choice == "1":
                return self._do_player_attack()
            if choice == "2":
                result = self._do_use_item()
                if result:
                    return result
            elif choice == "3":
                return self._do_run()
            else:
                print("  Enter 1, 2, or 3.")

    def _do_player_attack(self) -> str:
        base = self._player.attack + random.randint(-2, 5)
        if self._player.status_effects.get("speed_boost", 0) > 0:
            base = int(base * 1.5)
        crit = random.random() < 0.15
        if crit:
            base = int(base * 1.75)
        actual = self._enemy.take_damage(base)
        crit_label = "  *** CRITICAL HIT! ***  " if crit else ""
        print(f"\n  {crit_label}You strike {self._enemy.name} for {actual} damage!")
        return "attacked"

    def _do_use_item(self) -> str | None:
        consumables = self._inventory.get_consumables()
        if not consumables:
            print("  No usable items!")
            return None

        print("\n  Choose item:")
        for i, (item, qty) in enumerate(consumables):
            print(f"  [{i + 1}] {item.name} x{qty}  —  {item.description}")
        print("  [0] Cancel")

        while True:
            raw = input("\n  > ").strip()
            if raw == "0":
                return None
            try:
                idx = int(raw) - 1
                if 0 <= idx < len(consumables):
                    item, _ = consumables[idx]
                    inv_idx = next(
                        j for j, (it, _) in enumerate(self._inventory.items)
                        if it.item_id == item.item_id
                    )
                    msg = self._inventory.use_item(inv_idx, self._player)
                    print(f"\n  {msg}")
                    return "used_item"
                print("  Invalid choice.")
            except ValueError:
                print("  Enter a number.")

    def _do_run(self) -> str:
        run_chance = max(0.20, 0.70 - self._enemy.level * 0.04)
        if random.random() < run_chance:
            print("\n  You successfully fled!")
            return "ran"
        print("\n  Couldn't escape!")
        return "failed_run"

    def _enemy_turn(self) -> None:
        if self._enemy.is_stunned():
            print(f"\n  {self._enemy.name} is stunned and cannot act!")
            return
        action = self._enemy.get_action()
        if action == "special":
            self._enemy_special()
        else:
            self._enemy_normal_attack()

    def _enemy_normal_attack(self) -> None:
        damage = self._enemy.attack + random.randint(-2, 3)
        actual = self._player.take_damage(damage)
        print(f"\n  {self._enemy.name} attacks you for {actual} damage!")

    def _enemy_special(self) -> None:
        ability = self._enemy.special_ability
        name = self._enemy.name

        if ability == "magic_bolt":
            raw = self._enemy.attack + random.randint(5, 15)
            actual = self._player.take_magic_damage(raw)
            print(f"\n  {name} casts Magic Bolt!  You take {actual} magic damage!")

        elif ability == "poison":
            actual = self._player.take_damage(self._enemy.attack + random.randint(0, 4))
            self._player.apply_status("poison", 3)
            print(f"\n  {name} bites you for {actual} damage and poisons you! (3 turns)")

        elif ability == "stun":
            actual = self._player.take_damage(self._enemy.attack)
            self._player.apply_status("stun", 1)
            print(f"\n  {name} stuns you for {actual} damage! You lose your next turn!")

        elif ability == "shadow_army":
            raw = self._enemy.attack * 2
            actual = self._player.take_magic_damage(raw)
            print(f"\n  {name} unleashes the SHADOW ARMY!  You take {actual} damage!")

        else:
            self._enemy_normal_attack()

    def run(self) -> str:
        print("\n" + "═" * 50)
        print("  ⚔   C O M B A T   ⚔")
        print("═" * 50)
        self._print_status()

        while self._player.is_alive and self._enemy.is_alive:
            self._turn += 1
            print(f"\n  ── Turn {self._turn} ──")

            for msg in self._player.process_status_effects():
                print(f"  {msg}")
            if not self._player.is_alive:
                break

            if self._player.is_stunned():
                print(f"  You are stunned and skip your turn!")
            else:
                action = self._player_turn()
                if action == "ran":
                    return CombatResult.RAN

            if not self._enemy.is_alive:
                break

            for msg in self._enemy.process_status_effects():
                print(f"  {msg}")
            if not self._enemy.is_alive:
                break

            self._enemy_turn()

            if self._player.is_alive and self._enemy.is_alive:
                self._print_status()

        if self._player.is_alive:
            print(f"\n  ★  Victory!  You defeated {self._enemy.name}!  ★")
            return CombatResult.WIN
        print(f"\n  ✗  Defeated...  {self._enemy.name} was too strong.")
        return CombatResult.LOSE
