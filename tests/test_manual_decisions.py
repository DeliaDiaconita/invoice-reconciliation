from manual_decisions import apply_rejected_matches, apply_accepted_matches


def test_reject_only_possible_payment_moves_invoice_to_unmatched():
    invoices = [
        {
            "invoice_number": "INV001",
            "client": "Ana Popescu",
            "amount": 500.0,
            "issue_date": "05.09.2026",
        }
    ]

    payment = {
        "payment_id": "P001",
        "name": "Mihai Popescu",
        "amount": 500.0,
        "payment_date": "10.09.2026",
        "description": "plata septembrie",
    }

    results = {
        "direct_matches": [],
        "possible_matches_by_invoice": {
            "INV001": {
                "client": "Ana Popescu",
                "payments": [payment],
            }
        },
        "unmatched": [],
    }

    rejected_matches = {("INV001", "P001")}

    apply_rejected_matches(
        results,
        invoices,
        rejected_matches,
    )

    assert "INV001" not in results["possible_matches_by_invoice"]

    assert len(results["unmatched"]) == 1
    assert results["unmatched"][0]["invoice_number"] == "INV001"

    assert len(results["direct_matches"]) == 0
    print(
        "Test passed: Rejecting the only possible payment moves the invoice to unmatched."
    )


def test_reject_one_of_two_possible_payments_keeps_invoice_possible():
    invoices = [
        {
            "invoice_number": "INV001",
            "client": "Ana Popescu",
            "amount": 500.0,
            "issue_date": "05.09.2026",
        }
    ]

    payment_1 = {
        "payment_id": "P001",
        "name": "Mihai Popescu",
        "amount": 500.0,
        "payment_date": "10.09.2026",
        "description": "plata",
    }

    payment_2 = {
        "payment_id": "P002",
        "name": "Ion Popescu",
        "amount": 500.0,
        "payment_date": "11.09.2026",
        "description": "plata",
    }

    results = {
        "direct_matches": [],
        "possible_matches_by_invoice": {
            "INV001": {
                "client": "Ana Popescu",
                "payments": [
                    payment_1,
                    payment_2,
                ],
            }
        },
        "unmatched": [],
    }

    rejected_matches = {("INV001", "P001")}

    apply_rejected_matches(
        results,
        invoices,
        rejected_matches,
    )

    assert "INV001" in results["possible_matches_by_invoice"]

    remaining_payments = results["possible_matches_by_invoice"]["INV001"]["payments"]

    assert len(remaining_payments) == 1
    assert remaining_payments[0]["payment_id"] == "P002"

    assert len(results["unmatched"]) == 0
    print(
        "Test passed: Rejecting one of two possible payments keeps the invoice in possible matches."
    )


def test_accept_possible_match_moves_it_to_direct():
    invoices = [
        {
            "invoice_number": "INV001",
            "client": "Ana Popescu",
            "amount": 500.0,
            "issue_date": "05.09.2026",
        }
    ]

    payment = {
        "payment_id": "P001",
        "name": "Mihai Popescu",
        "amount": 500.0,
        "payment_date": "10.09.2026",
        "description": "plata",
    }

    results = {
        "direct_matches": [],
        "possible_matches_by_invoice": {
            "INV001": {
                "client": "Ana Popescu",
                "payments": [payment],
            }
        },
        "unmatched": [],
    }

    accepted_matches = {("INV001", "P001")}

    apply_accepted_matches(
        results,
        invoices,
        accepted_matches,
    )

    assert "INV001" not in results["possible_matches_by_invoice"]

    assert len(results["direct_matches"]) == 1

    direct_match = results["direct_matches"][0]

    assert direct_match["invoice_number"] == "INV001"
    assert direct_match["payment_id"] == "P001"
    assert direct_match["client"] == "Ana Popescu"
    assert direct_match["payer_name"] == "Mihai Popescu"

    assert len(results["unmatched"]) == 0
    print("Test passed: Accepting a possible match moves it to direct matches.")


def test_accepted_payment_is_removed_from_other_invoices():
    invoices = [
        {
            "invoice_number": "INV001",
            "client": "Ana Popescu",
            "amount": 500.0,
            "issue_date": "05.09.2026",
        },
        {
            "invoice_number": "INV002",
            "client": "Maria Popescu",
            "amount": 500.0,
            "issue_date": "05.09.2026",
        },
    ]

    payment = {
        "payment_id": "P001",
        "name": "Mihai Popescu",
        "amount": 500.0,
        "payment_date": "10.09.2026",
        "description": "plata",
    }

    results = {
        "direct_matches": [],
        "possible_matches_by_invoice": {
            "INV001": {
                "client": "Ana Popescu",
                "payments": [payment],
            },
            "INV002": {
                "client": "Maria Popescu",
                "payments": [payment],
            },
        },
        "unmatched": [],
    }

    accepted_matches = {("INV001", "P001")}

    apply_accepted_matches(
        results,
        invoices,
        accepted_matches,
    )

    # INV001 a fost acceptata
    assert len(results["direct_matches"]) == 1
    assert results["direct_matches"][0]["invoice_number"] == "INV001"

    # INV001 nu mai este Possible
    assert "INV001" not in results["possible_matches_by_invoice"]

    # P001 a fost consumata, deci INV002 nu mai are candidat
    assert "INV002" not in results["possible_matches_by_invoice"]

    # INV002 devine neplatita
    assert len(results["unmatched"]) == 1
    assert results["unmatched"][0]["invoice_number"] == "INV002"
    print(
        "Test passed: Accepting a payment for one invoice removes it from other invoices and moves them to unmatched."
    )
