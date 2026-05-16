import os
import sys
import time
import random

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

from config.db import load_csv, get_entity_by_field, add_entry
from models.character import Player, Enemy
from models.items import ItemFactory, Item, Potion
from systems.inventory import Inventory
from systems.combat import CombatSystem, CombatResult
from systems.exploration import ExplorationSystem
from services.save_load import save_game, load_game, has_save
from services.event_system import EventSystem


BANNER = r"""
╔══════════════════════════════════════════════════╗
║                                                  ║
║   ░██████╗██╗  ██╗░█████╗░██████╗  ░██╗░░░██╗  ║
║   ██╔════╝██║  ██║██╔══██╗██╔══██╗ ░██║░░░██║  ║
║   ╚█████╗ ███████║███████║██║  ██║ ░██║░░░██║  ║
║   ░╚═══██╗██╔══██║██╔══██║██║  ██║ ░██║░░░██║  ║
║   ██████╔╝██║  ██║██║  ██║██████╔╝ ░███████╔╝  ║
║   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚══════╝   ║
║                                                  ║
║          L E V E L I N G   R P G                ║
╚══════════════════════════════════════════════════╝
"""


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def pause(msg: str = "  Press Enter to continue...") -> None:
    input(f"\n{msg}")


def load_game_data() -> tuple[list[Enemy], dict[int, Item]]:
    enemies: list[Enemy] = []
    for row in load_csv("enemies"):
        try:
            enemies.append(Enemy.from_dict(row))
        except Exception as e:
            print(f"  [Warning] Could not load enemy row: {e}")

    items: dict[int, Item] = {}
    for row in load_csv("items"):
        try:
            item = ItemFactory.create(row)
            items[item.item_id] = item
        except Exception as e:
            print(f"  [Warning] Could not load item row: {e}")

    return enemies, items


def _login() -> str | None:
    print("\n  ─── Login ───")
    username = input("  Username : ").strip()
    password = input("  Password : ").strip()
    record = get_entity_by_field("users", "username", username)
    if record and record.get("password") == password:
        print(f"\n  Welcome back, {username}!")
        time.sleep(0.8)
        return username
    print("  Invalid credentials.")
    pause()
    return None


def _register() -> str | None:
    print("\n  ─── Register ───")
    username = input("  Choose username (min 2 chars) : ").strip()
    if len(username) < 2:
        print("  Username too short.")
        pause()
        return None
    if get_entity_by_field("users", "username", username):
        print("  Username already taken.")
        pause()
        return None
    password = input("  Choose password (min 4 chars) : ").strip()
    if len(password) < 4:
        print("  Password too short.")
        pause()
        return None
    add_entry("users", {"username": username, "password": password})
    print(f"\n  Account created! Welcome, {username}!")
    time.sleep(0.8)
    return username


def auth_screen() -> str | None:
    clear()
    print(BANNER)
    print("  [1] Login")
    print("  [2] Register")
    print("  [3] Exit")

    while True:
        choice = input("\n  > ").strip()
        if choice == "1":
            return _login()
        if choice == "2":
            return _register()
        if choice == "3":
            print("\n  Farewell, Hunter...")
            sys.exit(0)
        print("  Enter 1, 2, or 3.")


def start_new_game(username: str, items: dict[int, Item]) -> tuple[Player, Inventory]:
    clear()
    print("\n  ─── New Hunter ───")
    name = input("  Enter your hunter name: ").strip() or username
    player = Player(name=name)
    inventory = Inventory()
    if 1 in items:
        inventory.add_item(items[1], 2)
    else:
        inventory.add_item(Potion(1, "Health Potion", 30, "Restores 30 HP", "common", 20), 2)
    print(f"\n  Hunter '{name}' has awakened!")
    print(f"  Stats  —  HP: {player.max_hp}  ATK: {player.attack}  DEF: {player.defense}")
    print(f"  Starting items: 2× Health Potion")
    pause()
    return player, inventory


def choose_save_or_new(username: str, items: dict[int, Item]) -> tuple[Player, Inventory]:
    clear()
    print(f"\n  Save file found for '{username}'.")
    print("  [1] Continue")
    print("  [2] New Game")
    while True:
        choice = input("\n  > ").strip()
        if choice == "1":
            result = load_game(username, items)
            if result:
                player, inventory = result
                print(f"\n  Welcome back, {player.name}!  [Lv.{player.level}]")
                time.sleep(0.8)
                return player, inventory
            print("  Could not load save. Starting new game.")
            return start_new_game(username, items)
        if choice == "2":
            return start_new_game(username, items)
        print("  Enter 1 or 2.")


def _bar(current: int, maximum: int, width: int = 15) -> str:
    filled = int((current / max(1, maximum)) * width)
    return "█" * filled + "░" * (width - filled)


def _header_bar(player: Player) -> None:
    hp_bar = _bar(player.hp, player.max_hp)
    xp_bar = _bar(player.xp, player.xp_to_next, 10)
    print(f"  {player.name}  Lv.{player.level}  │  "
          f"HP [{hp_bar}] {player.hp}/{player.max_hp}  │  "
          f"XP [{xp_bar}] {player.xp}/{player.xp_to_next}  │  "
          f"Gold: {player.gold}G  │  Kills: {player.kills}")
    if player.status_effects:
        effects = "  ".join(f"{k}({v}t)" for k, v in player.status_effects.items())
        print(f"  Status: {effects}")


def show_stats(player: Player, inventory: Inventory) -> None:
    clear()
    print("\n" + "═" * 50)
    print("  ★  H U N T E R   S T A T U S  ★")
    print("═" * 50)
    xp_bar = _bar(player.xp, player.xp_to_next, 20)
    print(f"\n  Name     : {player.name}")
    print(f"  Level    : {player.level}")
    print(f"  HP       : {player.hp}/{player.max_hp}")
    print(f"  Attack   : {player.attack}"
          + (f"  (weapon +{player._weapon_bonus})" if player._weapon_bonus else ""))
    print(f"  Defense  : {player.defense}"
          + (f"  (armor  +{player._armor_bonus})" if player._armor_bonus else ""))
    print(f"  XP       : [{xp_bar}] {player.xp}/{player.xp_to_next}")
    print(f"  Gold     : {player.gold}G")
    print(f"  Kills    : {player.kills}")
    if player.equipped_weapon:
        print(f"\n  Weapon   : {player.equipped_weapon.name}")
    if player.equipped_armor:
        print(f"  Armor    : {player.equipped_armor.name}")
    if player.status_effects:
        effects = "  ".join(f"{k}({v}t)" for k, v in player.status_effects.items())
        print(f"\n  Effects  : {effects}")
    print(f"\n  ─── Inventory  ({len(inventory)}/{inventory.MAX_SIZE} slots) ───")
    print(inventory.display())
    print()
    pause()


def manage_inventory(player: Player, inventory: Inventory) -> None:
    while True:
        clear()
        print("\n" + "═" * 50)
        print(f"  ★  I N V E N T O R Y  ({len(inventory)}/{inventory.MAX_SIZE})  ★")
        print("═" * 50)
        print(inventory.display())
        print("\n  [1] Use / Equip item")
        print("  [2] Back")
        choice = input("\n  > ").strip()

        if choice == "1":
            if not inventory.items:
                print("  Inventory is empty.")
                pause()
                continue
            raw = input("  Item number: ").strip()
            try:
                idx = int(raw) - 1
                msg = inventory.use_item(idx, player)
                print(f"\n  {msg}")
            except ValueError:
                print("  Enter a valid number.")
            pause()
        elif choice == "2":
            break


def explore(
    username: str,
    player: Player,
    inventory: Inventory,
    exploration: ExplorationSystem,
    event_sys: EventSystem,
) -> None:
    zone = exploration.choose_zone(player.level)
    print(f"\n  Entering: {zone.name}...")
    time.sleep(0.6)

    event_type = exploration.roll_event(zone)

    if event_type == "encounter":
        enemy = exploration.get_encounter_enemy(zone, player.level)
        print(f"\n  ⚠  A {enemy.name} blocks your path!  [Rank {enemy.rank}]")
        time.sleep(0.8)

        result = CombatSystem(player, enemy, inventory).run()

        if result == CombatResult.WIN:
            gold_drop = enemy.gold_reward + random.randint(0, 10)
            player.add_kill()
            player.add_gold(gold_drop)
            xp_msgs = player.gain_xp(enemy.xp_reward)
            print(f"\n  Rewards:")
            print(f"  +{gold_drop} Gold")
            for msg in xp_msgs:
                print(f"  {msg}")
            if random.random() < 0.35:
                loot = exploration.get_loot(player.level)
                if loot:
                    print(f"\n  Item drop: {inventory.add_item(loot)}")
            _autosave(username, player, inventory)

        elif result == CombatResult.LOSE:
            print("\n  You crawl back to safety with 1 HP remaining...")
            player._hp = 1
            _autosave(username, player, inventory)

        pause()

    elif event_type == "loot":
        loot = exploration.get_loot(player.level)
        if loot:
            print(f"\n  ✦  You found: {loot.name}  [{loot.rarity}]")
            print(f"  {loot.description}")
            print(f"  {inventory.add_item(loot)}")
            _autosave(username, player, inventory)
        pause()

    elif event_type == "special":
        event = exploration.special_event(player.level)
        print(f"\n  ★  Special Event!  ★")
        print(f"  {event['text']}")
        reward = event.get("reward", {})
        if "gold" in reward:
            player.add_gold(reward["gold"])
            print(f"  +{reward['gold']} Gold!")
        if reward.get("hp") == "full":
            player.heal(player.max_hp)
            print(f"  HP fully restored!")
        if "xp" in reward:
            for msg in player.gain_xp(reward["xp"]):
                print(f"  {msg}")
        print(f"\n  {event_sys.trigger_special_message(event)}")
        _autosave(username, player, inventory)
        pause()

    else:
        msg = event_sys.trigger_empty_event()
        print(f"\n  {msg}")
        hp_gain = event_sys.heal_from_empty_event(msg)
        if hp_gain:
            player.heal(hp_gain)
            print(f"  HP: {player.hp}/{player.max_hp}")
        pause()


def _autosave(username: str, player: Player, inventory: Inventory) -> None:
    if save_game(username, player, inventory):
        print("  [Auto-saved]")


def game_loop(
    username: str,
    player: Player,
    inventory: Inventory,
    exploration: ExplorationSystem,
    event_sys: EventSystem,
) -> None:
    while True:
        clear()
        print(BANNER)
        _header_bar(player)
        print("\n" + "─" * 50)
        print("  [1] Explore")
        print("  [2] Inventory")
        print("  [3] Stats")
        print("  [4] Save Game")
        print("  [5] Quit")

        choice = input("\n  > ").strip()

        if choice == "1":
            explore(username, player, inventory, exploration, event_sys)
        elif choice == "2":
            manage_inventory(player, inventory)
        elif choice == "3":
            show_stats(player, inventory)
        elif choice == "4":
            ok = save_game(username, player, inventory)
            print("\n  ✓ Game saved!" if ok else "\n  ✗ Save failed.")
            pause()
        elif choice == "5":
            print("\n  Saving before exit...")
            save_game(username, player, inventory)
            print("  Farewell, Hunter...")
            time.sleep(0.8)
            break
        else:
            print("  Enter 1–5.")
            time.sleep(0.4)


def main() -> None:
    while True:
        username = auth_screen()
        if not username:
            continue

        enemies, items = load_game_data()
        if not enemies:
            print("  [Error] enemies.csv is empty or missing. Cannot start game.")
            pause()
            continue

        exploration = ExplorationSystem(enemies, items)
        event_sys = EventSystem()

        if has_save(username):
            player, inventory = choose_save_or_new(username, items)
        else:
            player, inventory = start_new_game(username, items)

        game_loop(username, player, inventory, exploration, event_sys)
        break


if __name__ == "__main__":
    main()
