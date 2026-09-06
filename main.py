from imports import load_invoices, load_payments
from reconciliation import reconcile
from relations import load_relations


# AFISARE REZULTATE
def print_report(results):
    print("\n=== DIRECT MATCHES ===")

    for match in results["direct_matches"]:
        print(
            "Factura",
            match["invoice_number"],
            "pentru",
            match["client"],
            "-> DIRECT MATCH ->",
            "plata",
            match["payment_id"],
            "efectuata de",
            match["payer_name"],
            "in data de",
            match["payment_date"],
        )

    print("\n=== POSSIBLE MATCHES ===")

    for invoice_number, data in results["possible_matches_by_invoice"].items():
        print(
            "Factura", invoice_number, "pentru", data["client"], "-> POSSIBLE MATCHES:"
        )

        for payment in data["payments"]:
            print(
                "   Plata",
                payment["payment_id"],
                "efectuata de",
                payment["name"],
                "la data de",
                payment["payment_date"],
            )

    print("\n=== UNMATCHED ===")

    for invoice in results["unmatched"]:
        print(
            "Factura",
            invoice["invoice_number"],
            "pentru",
            invoice["client"],
            "-> UNMATCHED",
        )


if __name__ == "__main__":
    invoices = load_invoices("Lista_facturi.xlsx")
    payments = load_payments("payments.csv")

    confirmed_relations = load_relations()
    results = reconcile(invoices, payments, confirmed_relations)

    print_report(results)
"""

"""
