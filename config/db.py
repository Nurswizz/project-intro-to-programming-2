import csv
import os

BASE_URL = "./data"

URLS = {
    "users": f"{BASE_URL}/users.csv",
    "items": f"{BASE_URL}/items.csv",
    "enemies": f"{BASE_URL}/enemies.csv",
    "player_saves": f"{BASE_URL}/player_saves.csv",
    "inventory_saves": f"{BASE_URL}/inventory_saves.csv",
}


def load_csv(filename: str) -> list[dict]:
    path = URLS.get(filename)
    if not path or not os.path.exists(path):
        return []
    with open(path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def save_csv(filename: str, rows: list[dict], fieldnames: list[str]) -> None:
    path = URLS.get(filename)
    if not path:
        return
    with open(path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        if rows:
            writer.writerows(rows)


def add_entry(filename: str, entry: dict) -> None:
    path = URLS.get(filename)
    if not path:
        return
    file_exists = os.path.exists(path) and os.path.getsize(path) > 0
    with open(path, mode="a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=entry.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry)


def get_entity_by_field(filename: str, field: str, value) -> dict | None:
    for entry in load_csv(filename):
        if entry.get(field) == str(value):
            return entry
    return None


def get_all_by_field(filename: str, field: str, value) -> list[dict]:
    return [e for e in load_csv(filename) if e.get(field) == str(value)]


def update_entity(filename: str, field: str, value, updated_entry: dict) -> None:
    entries = load_csv(filename)
    fieldnames = list(updated_entry.keys())
    for i, entry in enumerate(entries):
        if entry.get(field) == str(value):
            entries[i] = updated_entry
            break
    save_csv(filename, entries, fieldnames)


def delete_entity(filename: str, field: str, value) -> None:
    entries = load_csv(filename)
    if not entries:
        return
    fieldnames = list(entries[0].keys())
    entries = [e for e in entries if e.get(field) != str(value)]
    save_csv(filename, entries, fieldnames)


def delete_all_by_field(filename: str, field: str, value) -> None:
    entries = load_csv(filename)
    if not entries:
        return
    fieldnames = list(entries[0].keys())
    entries = [e for e in entries if e.get(field) != str(value)]
    save_csv(filename, entries, fieldnames)
