import csv
import os
from config.db import (
    load_csv, save_csv, add_entry, get_entity_by_field,
    update_entity, get_all_by_field, delete_all_by_field, URLS,
)
from models.character import Player
from models.items import Item
from systems.inventory import Inventory


_PLAYER_FIELDS = [
    "username", "name", "hp", "max_hp", "attack", "defense",
    "level", "xp", "xp_to_next", "gold", "kills",
    "weapon_bonus", "armor_bonus", "equipped_weapon_id", "equipped_armor_id",
]

_INVENTORY_FIELDS = ["username", "item_id", "quantity"]


def _ensure_save_files() -> None:
    specs = {
        "player_saves": _PLAYER_FIELDS,
        "inventory_saves": _INVENTORY_FIELDS,
    }
    for key, fields in specs.items():
        path = URLS[key]
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                csv.DictWriter(fh, fieldnames=fields).writeheader()


def save_game(username: str, player: Player, inventory: Inventory) -> bool:
    try:
        _ensure_save_files()
        row = {"username": username, **player.to_dict()}
        if get_entity_by_field("player_saves", "username", username):
            update_entity("player_saves", "username", username, row)
        else:
            add_entry("player_saves", row)

        delete_all_by_field("inventory_saves", "username", username)
        for entry in inventory.to_list():
            add_entry("inventory_saves", {
                "username": username,
                "item_id": str(entry["item_id"]),
                "quantity": str(entry["quantity"]),
            })
        return True
    except Exception as exc:
        print(f"  [Save error] {exc}")
        return False


def load_game(username: str, all_items: dict[int, Item]) -> tuple[Player, Inventory] | None:
    try:
        _ensure_save_files()
        data = get_entity_by_field("player_saves", "username", username)
        if not data:
            return None

        player = Player.from_dict(data)

        inventory = Inventory()
        for row in get_all_by_field("inventory_saves", "username", username):
            item_id = int(row["item_id"])
            qty = int(row["quantity"])
            if item_id in all_items:
                inventory.add_item(all_items[item_id], qty)

        for attr, method in (("equipped_weapon_id", "equip_weapon"),
                             ("equipped_armor_id",  "equip_armor")):
            saved_id = data.get(attr, "none")
            if saved_id != "none":
                item = all_items.get(int(saved_id))
                if item:
                    getattr(player, method)(item)

        return player, inventory
    except Exception as exc:
        print(f"  [Load error] {exc}")
        return None


def has_save(username: str) -> bool:
    try:
        _ensure_save_files()
        return get_entity_by_field("player_saves", "username", username) is not None
    except Exception:
        return False
