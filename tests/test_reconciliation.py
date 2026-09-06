# TESTARE
from main import reconcile


def test_basic_reconciliation():
    test_invoices = [
        {
            "invoice_number": "INV001",
            "client": "Ana Popescu",
            "amount": 1775,
            "issue_date": "05.09.2026",
        },
        {
            "invoice_number": "INV002",
            "client": "Maria Ionescu",
            "amount": 2500,
            "issue_date": "10.09.2026",
        },
        {
            "invoice_number": "INV003",
            "client": "Ion Georgescu",
            "amount": 3200,
            "issue_date": "15.11.2026",
        },
    ]

    test_payments = [
        {
            "payment_id": 1,
            "name": "Mihai Popescu",
            "description": "after septembrie",
            "amount": 1775,
            "payment_date": "07.09.2026",
        },
        {
            "payment_id": 2,
            "name": "Andrei Ionescu",
            "description": "plata factura INV002",
            "amount": 2500,
            "payment_date": "12.09.2026",
        },
    ]

    results = reconcile(test_invoices, test_payments)

    assert len(results["direct_matches"]) == 1
    assert len(results["possible_matches_by_invoice"]) == 1
    assert len(results["unmatched"]) == 1
    assert results["direct_matches"][0]["invoice_number"] == "INV002"
    assert "INV001" in results["possible_matches_by_invoice"]
    assert results["unmatched"][0]["invoice_number"] == "INV003"
    print("Test basic reconciliation passed!")  # nu se printeaza daca nu ajunge aici


def test_amount_mismatch():
    test_invoices = [
        {
            "invoice_number": "INV001",
            "client": "Ana Popescu",
            "amount": 1775,
            "issue_date": "05.09.2026",
        }
    ]

    test_payments = [
        {
            "payment_id": 1,
            "name": "Mihai Popescu",
            "description": "after septembrie",
            "amount": 1800,
            "payment_date": "07.09.2026",
        }
    ]

    results = reconcile(test_invoices, test_payments)

    assert len(results["direct_matches"]) == 0
    assert len(results["possible_matches_by_invoice"]) == 0
    assert len(results["unmatched"]) == 1
    print("Test amount mismatch passed!")


def test_late_payment_with_month_in_description():
    test_invoices = [
        {
            "invoice_number": "INV001",
            "client": "Ana Popescu",
            "amount": 1775,
            "issue_date": "05.09.2026",
        }
    ]

    test_payments = [
        {
            "payment_id": 1,
            "name": "Mihai Popescu",
            "description": "after septembrie",
            "amount": 1775,
            "payment_date": "07.10.2026",
        }
    ]

    results = reconcile(test_invoices, test_payments)
    assert len(results["direct_matches"]) == 0
    assert len(results["possible_matches_by_invoice"]) == 1
    assert len(results["unmatched"]) == 0
    assert "INV001" in results["possible_matches_by_invoice"]
    print("Test late payment with month in description passed!")


def test_direct_match_payment_not_reused():
    test_invoices = [
        {
            "invoice_number": "INV001",
            "client": "Ana Ionescu",
            "amount": 2500,
            "issue_date": "05.09.2026",
        },
        {
            "invoice_number": "INV002",
            "client": "Maria Ionescu",
            "amount": 2500,
            "issue_date": "10.09.2026",
        },
    ]

    test_payments = [
        {
            "payment_id": 1,
            "name": "Andrei Ionescu",
            "description": "plata factura INV002",
            "amount": 2500,
            "payment_date": "12.09.2026",
        }
    ]

    results = reconcile(test_invoices, test_payments)

    assert len(results["direct_matches"]) == 1
    assert len(results["possible_matches_by_invoice"]) == 0
    assert len(results["unmatched"]) == 1
    assert results["direct_matches"][0]["invoice_number"] == "INV002"
    assert results["direct_matches"][0]["payment_id"] == 1
    assert results["unmatched"][0]["invoice_number"] == "INV001"

    print("Test direct match payment not reused passed!")


def test_ambiguous_possible_match():
    test_invoices = [
        {
            "invoice_number": "INV001",
            "client": "Ana Popescu",
            "amount": 1775,
            "issue_date": "05.09.2026",
        },
        {
            "invoice_number": "INV002",
            "client": "Ioana Popescu",
            "amount": 1775,
            "issue_date": "08.09.2026",
        },
    ]

    test_payments = [
        {
            "payment_id": 1,
            "name": "Mihai Popescu",
            "description": "after septembrie",
            "amount": 1775,
            "payment_date": "10.09.2026",
        }
    ]

    results = reconcile(test_invoices, test_payments)
    assert len(results["direct_matches"]) == 0
    assert len(results["possible_matches_by_invoice"]) == 2
    assert len(results["unmatched"]) == 0
    assert "INV001" in results["possible_matches_by_invoice"]
    assert "INV002" in results["possible_matches_by_invoice"]
    assert (
        results["possible_matches_by_invoice"]["INV001"]["payments"][0]["payment_id"]
        == 1
    )
    assert (
        results["possible_matches_by_invoice"]["INV002"]["payments"][0]["payment_id"]
        == 1
    )
    print("Test ambiguous possible match passed!")


def test_exact_name_direct_match():
    test_invoices = [
        {
            "invoice_number": "INV001",
            "client": "Ana Popescu",
            "amount": 1775,
            "issue_date": "05.09.2026",
        }
    ]

    test_payments = [
        {
            "payment_id": 1,
            "name": "Popescu Ana",
            "description": "after",
            "amount": 1775,
            "payment_date": "07.09.2026",
        }
    ]

    results = reconcile(test_invoices, test_payments)

    assert len(results["direct_matches"]) == 1
    assert len(results["possible_matches_by_invoice"]) == 0
    assert len(results["unmatched"]) == 0

    assert results["direct_matches"][0]["invoice_number"] == "INV001"
    assert results["direct_matches"][0]["payment_id"] == 1
    print("Test exact name direct match passed!")


def test_confirmed_relation_direct_match():
    test_invoices = [
        {
            "invoice_number": "INV001",
            "client": "Ana Popescu",
            "amount": 1775,
            "issue_date": "05.09.2026",
        }
    ]

    test_payments = [
        {
            "payment_id": 1,
            "name": "Mihai Popescu",
            "description": "after",
            "amount": 1775,
            "payment_date": "07.09.2026",
        }
    ]

    test_relations = [
        {
            "payer_name": "Mihai Popescu",
            "client": "Ana Popescu",
        }
    ]

    results = reconcile(
        test_invoices,
        test_payments,
        test_relations,
    )

    assert len(results["direct_matches"]) == 1
    assert len(results["possible_matches_by_invoice"]) == 0
    assert len(results["unmatched"]) == 0

    assert results["direct_matches"][0]["invoice_number"] == "INV001"
    assert results["direct_matches"][0]["payment_id"] == 1
    print("Test confirmed relation direct match passed!")
