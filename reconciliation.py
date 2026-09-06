from datetime import datetime

months = {
    1: "ianuarie",
    2: "februarie",
    3: "martie",
    4: "aprilie",
    5: "mai",
    6: "iunie",
    7: "iulie",
    8: "august",
    9: "septembrie",
    10: "octombrie",
    11: "noiembrie",
    12: "decembrie",
}


def normalize_name(name):
    return set(name.lower().split())


def is_confirmed_relation(client, payer_name, confirmed_relations):
    client_parts = normalize_name(client)
    payer_parts = normalize_name(payer_name)

    for relation in confirmed_relations:
        relation_client = normalize_name(relation["client"])
        relation_payer = normalize_name(relation["payer_name"])

        if client_parts == relation_client and payer_parts == relation_payer:
            return True

    return False


def compare_invoice_payment(invoice, payment):

    # NUME
    client_parts = normalize_name(invoice["client"])
    payer_parts = normalize_name(payment["name"])
    common_parts = client_parts & payer_parts
    exact_match = client_parts == payer_parts

    # DETERMINARE DATE SI LUNA
    invoice_date = datetime.strptime(invoice["issue_date"], "%d.%m.%Y").date()
    payment_date = datetime.strptime(payment["payment_date"], "%d.%m.%Y").date()
    invoice_month = months[invoice_date.month]
    same_issue_payment_month = (
        invoice_date.year == payment_date.year
        and invoice_date.month == payment_date.month
    )
    # SUMA
    same_amount = invoice["amount"] == payment["amount"]
    # NUMAR FACTURA SI LUNA IN DESCRIERE
    invoice_number_found = (
        invoice["invoice_number"].lower() in payment["description"].lower()
    )
    month_found_in_description = invoice_month in payment["description"].lower()

    return {
        "common_parts": common_parts,
        "same_amount": same_amount,
        "same_issue_payment_month": same_issue_payment_month,
        "invoice_number_found": invoice_number_found,
        "month_found_in_description": month_found_in_description,
        "exact_match": exact_match,
    }


# VERIFICARE POTRIVIRE DIRECTA
def direct_match_pass(
    invoices,
    payments,
    confirmed_relations,
    matched_payment_ids,
    matched_invoice_numbers,
    direct_matches,
):

    for invoice in invoices:

        if invoice["invoice_number"] in matched_invoice_numbers:
            continue

        for payment in payments:

            # VERIFICARE DACA PLATA A FOST DEJA POTRIVITA 100%
            if payment["payment_id"] in matched_payment_ids:
                continue

            # DETERMINARE CONDITII POTRIVIRE
            match = compare_invoice_payment(invoice, payment)
            confirmed_relation = is_confirmed_relation(
                invoice["client"],
                payment["name"],
                confirmed_relations,
            )
            # VERIFICARE CONDITII DE POTRIVIRE
            direct_match = (
                match["same_amount"]
                and match["same_issue_payment_month"]
                and (
                    match["invoice_number_found"]
                    or match["exact_match"]
                    or confirmed_relation
                )
            )
            if direct_match:
                matched_payment_ids.add(payment["payment_id"])
                matched_invoice_numbers.add(invoice["invoice_number"])

                direct_matches.append(
                    {
                        "invoice_number": invoice["invoice_number"],
                        "client": invoice["client"],
                        "payment_id": payment["payment_id"],
                        "payer_name": payment["name"],
                        "payment_date": payment["payment_date"],
                        "amount": payment["amount"],
                    }
                )

                break


# VERIFICARE POTRIVIRE 2
def possible_match_pass(
    invoices,
    payments,
    matched_payment_ids,
    matched_invoice_numbers,
    possible_matches_by_invoice,
    unmatched,
):
    for invoice in invoices:

        if invoice["invoice_number"] in matched_invoice_numbers:
            continue

        possible_matches = []

        for payment in payments:

            # VERIFICARE DACA PLATA A FOST DEJA POTRIVITA 100%
            if payment["payment_id"] in matched_payment_ids:
                continue

            # DETERMINARE CONDITII POTRIVIRE
            match = compare_invoice_payment(invoice, payment)

            possible_match = (
                match["same_amount"]
                and match["common_parts"]
                and (
                    match["same_issue_payment_month"]
                    or match["month_found_in_description"]
                )
            )

            # VERIFICARE CONDITII DE POTRIVIRE
            if possible_match:
                possible_matches.append(payment)

        # ADAUGA IN DICTIONARUL DE POSIBILE MATCH-URI SAU IN LISTA DE UNMATCHED
        if possible_matches:
            possible_matches_by_invoice[invoice["invoice_number"]] = {
                "client": invoice["client"],
                "payments": possible_matches,
            }
        else:
            unmatched.append(invoice)


def reconcile(invoices, payments, confirmed_relations=None):
    if confirmed_relations is None:
        confirmed_relations = []

    matched_payment_ids = set()
    matched_invoice_numbers = set()

    direct_matches = []
    possible_matches_by_invoice = {}
    unmatched = []

    # PAS 1: POTRIVIRE DIRECTA
    direct_match_pass(
        invoices,
        payments,
        confirmed_relations,
        matched_payment_ids,
        matched_invoice_numbers,
        direct_matches,
    )

    # PAS 2: POSIBILE MATCH-URI
    possible_match_pass(
        invoices,
        payments,
        matched_payment_ids,
        matched_invoice_numbers,
        possible_matches_by_invoice,
        unmatched,
    )

    return {
        "direct_matches": direct_matches,
        "possible_matches_by_invoice": possible_matches_by_invoice,
        "unmatched": unmatched,
    }
