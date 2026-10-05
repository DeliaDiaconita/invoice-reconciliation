def apply_rejected_matches(
    results,
    invoices,
    rejected_matches,
):
    # cream un dictionar pentru a accesa facturile dupa numarul facturii
    invoice_by_number = {invoice["invoice_number"]: invoice for invoice in invoices}
    for invoice_number, payment_id in rejected_matches:
        # verificam daca factura se mai afla in lista de posibile potriviri
        # daca nu mai exista, inseamna ca a fost deja acceptata sau respinsa
        if invoice_number not in results["possible_matches_by_invoice"]:
            continue

        # ia datele despre posibile potriviri pentru factura respectiva
        data = results["possible_matches_by_invoice"][invoice_number]

        # salvam plata respinsa inainte sa o stergem
        rejected_payment = None

        for payment in data["payments"]:
            if payment["payment_id"] == payment_id:
                rejected_payment = payment
                break

        # eliminam plata respinsa din lista de posibile potriviri
        data["payments"] = [
            payment
            for payment in data["payments"]
            if payment["payment_id"] != payment_id
        ]

        # verificam daca plata mai apare ca possible match la alta factura
        payment_still_possible = False

        for other_data in results["possible_matches_by_invoice"].values():

            for payment in other_data["payments"]:

                if payment["payment_id"] == payment_id:
                    payment_still_possible = True
                    break

            if payment_still_possible:
                break

        # daca plata nu mai apare nicaieri ca possible match,
        # o mutam in lista de incasari nematchuite
        if rejected_payment is not None and not payment_still_possible:

            if rejected_payment not in results["unmatched_payments"]:
                results["unmatched_payments"].append(rejected_payment)

        # daca nu mai exista plati posibile pentru factura respectiva, o mutam in lista de facturi neplatite
        if not data["payments"]:
            del results["possible_matches_by_invoice"][invoice_number]
            invoice = invoice_by_number[invoice_number]
            if invoice not in results["unmatched"]:
                results["unmatched"].append(invoice)


def apply_accepted_matches(
    results,
    invoices,
    accepted_matches,
):
    for invoice_number, payment_id in accepted_matches:

        # cream un dictionar pentru a accesa facturile dupa numarul facturii
        invoice_by_number = {invoice["invoice_number"]: invoice for invoice in invoices}

        # verificam daca factura se mai afla in lista de posibile potriviri
        if invoice_number not in results["possible_matches_by_invoice"]:
            continue

        # ia datele despre posibile potriviri pentru factura respectiva
        data = results["possible_matches_by_invoice"][invoice_number]

        accepted_payment = None

        #  cautam plata acceptata in lista de posibile potriviri
        # salvam datele ei in accepted_payment si iesim din bucla
        for payment in data["payments"]:
            if payment["payment_id"] == payment_id:
                accepted_payment = payment
                break

        # daca nu am gasit plata acceptata, inseamna ca a fost deja respinsa sau acceptata
        if accepted_payment is None:
            continue

        invoice = invoice_by_number[invoice_number]
        # mutam factura si plata acceptata in lista de potriviri directe
        results["direct_matches"].append(
            {
                "invoice_number": invoice_number,
                "client": invoice["client"],
                "payment_id": accepted_payment["payment_id"],
                "payer_name": accepted_payment["name"],
                "payment_date": accepted_payment["payment_date"],
                "amount": accepted_payment["amount"],
            }
        )
        # eliminam factura din lista de posibile potriviri
        del results["possible_matches_by_invoice"][invoice_number]

        # eliminam plata si din listele de possible potriviri pt alte facturi, daca exista
        invoices_to_unmatch = []

        for other_invoice_number, other_data in results[
            "possible_matches_by_invoice"
        ].items():
            # aici o scot
            other_data["payments"] = [
                payment
                for payment in other_data["payments"]
                if payment["payment_id"] != payment_id
            ]
            # daca nu mai exista plati posibile pentru factura respectiva, o mutam in lista de facturi neplatite
            if not other_data["payments"]:
                invoices_to_unmatch.append(other_invoice_number)

        # stergem facturile care nu mai au plati posibile
        for other_invoice_number in invoices_to_unmatch:
            # scot factura din lista de posibile potriviri
            del results["possible_matches_by_invoice"][other_invoice_number]
            # adaug factura in lista de facturi neplatite
            other_invoice = invoice_by_number[other_invoice_number]

            if other_invoice not in results["unmatched"]:
                results["unmatched"].append(other_invoice)

        # daca plata acceptata exista cumva si in unmatched_payments,
        # o eliminam
        results["unmatched_payments"] = [
            payment
            for payment in results["unmatched_payments"]
            if payment["payment_id"] != payment_id
        ]


def apply_unmatched_manual_matches(results, invoices, manual_unmatched_matches):
    invoice_by_number = {invoice["invoice_number"]: invoice for invoice in invoices}

    for invoice_number, payment_id in manual_unmatched_matches:

        # factura trebuie sa existe
        if invoice_number not in invoice_by_number:
            continue

        invoice = invoice_by_number[invoice_number]

        # factura trebuie sa fie in lista de facturi neplatite
        if invoice not in results["unmatched"]:
            continue

        matched_payment = None

        # cautam plata in lista de incasari nematchuite
        for payment in results["unmatched_payments"]:

            if payment["payment_id"] == payment_id:
                matched_payment = payment
                break

        # daca plata nu mai exista, nu facem nimic
        if matched_payment is None:
            continue

        # factura si plata trebuie sa aiba exact aceeasi suma
        if invoice["amount"] != matched_payment["amount"]:
            continue

        # eliminam factura din lista de facturi neplatite
        results["unmatched"] = [
            unmatched_invoice
            for unmatched_invoice in results["unmatched"]
            if unmatched_invoice["invoice_number"] != invoice_number
        ]

        # eliminam plata din lista de incasari nematchuite
        results["unmatched_payments"] = [
            payment
            for payment in results["unmatched_payments"]
            if payment["payment_id"] != payment_id
        ]


# face schimbari manuale in rezultatele reconcilerii
def apply_manual_decisions(
    results,
    invoices,
    accepted_matches,
    rejected_matches,
    manual_unmatched_matches,
):

    # am dat REJECT match
    apply_rejected_matches(results, invoices, rejected_matches)

    # am dat ACCEPT match
    apply_accepted_matches(
        results,
        invoices,
        accepted_matches,
    )

    # MATCH-URI MANUALE:
    # factura neplatita + incasare nematchuita
    apply_unmatched_manual_matches(
        results,
        invoices,
        manual_unmatched_matches,
    )

    return results
