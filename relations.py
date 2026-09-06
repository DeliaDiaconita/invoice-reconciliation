import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

RELATIONS_FILE = BASE_DIR / "data" / "confirmed_name_relations.json"


def canonical_name(name):
    return " ".join(sorted(name.lower().split()))


def load_relations():
    if not RELATIONS_FILE.exists():
        return []
    with open(RELATIONS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_relation(payer_name, client):
    relations = load_relations()

    payer_normalized = canonical_name(payer_name)
    client_normalized = canonical_name(client)
    # verificam daca relatia exista deja in lista de relatii
    for relation in relations:
        if (
            canonical_name(relation["payer_name"]) == payer_normalized
            and canonical_name(relation["client"]) == client_normalized
        ):
            return
    # o adauga daca nu exista
    relations.append({"payer_name": payer_name, "client": client})

    RELATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RELATIONS_FILE, "w", encoding="utf-8") as file:
        json.dump(relations, file, ensure_ascii=False, indent=4)
