import csv

BASE_URL = "./data"

URLS = { 
    "users": f"{BASE_URL}/users.csv",
    "items": f"{BASE_URL}/items.csv",
    "quests": f"{BASE_URL}/quests.csv",
}

def load_csv(filename):
    with open(URLS[filename], mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)

def add_entry(filename, entry):
    with open(URLS[filename], mode='a', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=entry.keys())
        writer.writerow(entry)

def get_entity_by_id(filename, entity_id):
    entries = load_csv(filename)
    for entry in entries:
        if entry['id'] == str(entity_id):
            return entry
    return None

def update_entity(filename, entity_id, updated_entry):
    entries = load_csv(filename)
    for i, entry in enumerate(entries):
        if entry['id'] == str(entity_id):
            entries[i] = updated_entry
            break
    with open(f"{BASE_URL}/{filename}", mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=updated_entry.keys())
        writer.writeheader()
        writer.writerows(entries)


def delete_entity(filename, entity_id):
    entries = load_csv(filename)
    entries = [entry for entry in entries if entry['id'] != str(entity_id)]
    with open(f"{BASE_URL}/{filename}", mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=entries[0].keys())
        writer.writeheader()
        writer.writerows(entries)