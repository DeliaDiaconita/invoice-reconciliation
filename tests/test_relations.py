import relations


def test_save_relation(tmp_path):
    # Cream un fisier JSON temporar doar pentru acest test.
    test_file = tmp_path / "confirmed_name_relations.json"

    # Facem ca functiile din relations.py sa foloseasca
    # fisierul temporar, nu fisierul real al aplicatiei.
    relations.RELATIONS_FILE = test_file

    relations.save_relation(
        "Mihai Popescu",
        "Ana Popescu",
    )

    saved_relations = relations.load_relations()

    assert len(saved_relations) == 1

    assert saved_relations[0]["payer_name"] == "Mihai Popescu"
    assert saved_relations[0]["client"] == "Ana Popescu"


def test_save_relation_does_not_create_duplicates(tmp_path):
    # Folosim un fisier temporar, nu fisierul real al aplicatiei.
    test_file = tmp_path / "confirmed_name_relations.json"
    relations.RELATIONS_FILE = test_file

    # Salvam aceeasi relatie de doua ori.
    relations.save_relation(
        "Mihai Popescu",
        "Ana Popescu",
    )

    relations.save_relation(
        "Mihai Popescu",
        "Ana Popescu",
    )

    saved_relations = relations.load_relations()

    # Trebuie sa existe o singura relatie.
    assert len(saved_relations) == 1


def test_save_relation_recognizes_reversed_name_order(tmp_path):
    # Folosim un fisier temporar pentru test.
    test_file = tmp_path / "confirmed_name_relations.json"
    relations.RELATIONS_FILE = test_file

    # Salvam relatia o data cu numele intr-o ordine.
    relations.save_relation(
        "Mihai Popescu",
        "Ana Popescu",
    )

    # Incercam sa salvam aceeasi relatie,
    # dar cu ordinea numelor inversata.
    relations.save_relation(
        "Popescu Mihai",
        "Popescu Ana",
    )

    saved_relations = relations.load_relations()

    # Relatia trebuie sa existe o singura data.
    assert len(saved_relations) == 1
