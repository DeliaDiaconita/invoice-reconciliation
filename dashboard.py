from imports import load_invoices, load_payments
from reconciliation import reconcile
import streamlit as st
from relations import load_relations, save_relation
from manual_decisions import apply_manual_decisions
from report import generate_report_pdf


# creaza in session state variabilele necesare daca nu exista deja
def initialize_session_state():
    if "results" not in st.session_state:
        st.session_state.results = None

    if "invoices" not in st.session_state:
        st.session_state.invoices = None

    if "accepted_matches" not in st.session_state:
        st.session_state.accepted_matches = set()

    if "rejected_matches" not in st.session_state:
        st.session_state.rejected_matches = set()


def process_files(invoice_file, payment_file):
    invoices = load_invoices(invoice_file)
    payments = load_payments(payment_file)

    confirmed_relations = load_relations()

    st.session_state.invoices = invoices

    st.session_state.results = reconcile(
        invoices,
        payments,
        confirmed_relations,
    )

    # Incepem o procesare noua, deci stergem deciziile
    # ramase de la procesarea precedenta.
    st.session_state.accepted_matches = set()
    st.session_state.rejected_matches = set()


def display_direct_matches(results):
    st.success("✅ FACTURI PLĂTITE")

    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 1.5, 1])

    col1.write("**Factură**")
    col2.write("**Client**")
    col3.write("**Plătitor**")
    col4.write("**Data plății**")
    col5.write("**Sumă**")

    for match in results["direct_matches"]:
        col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 1.5, 1])

        col1.write(match["invoice_number"])
        col2.write(match["client"])
        col3.write(match["payer_name"])
        col4.write(match["payment_date"])
        col5.write(f'{match["amount"]:.2f} lei')


def handle_accept(pair, payment, client):
    # memoram decizia pentru perechea factura-plata
    st.session_state.accepted_matches.add(pair)

    # ne asiguram ca aceeasi pereche nu este si respinsa
    st.session_state.rejected_matches.discard(pair)

    # memoram permanent relatia dintre platitor si client
    save_relation(
        payment["name"],
        client,
    )

    # rerulam dashboardul pentru aplicarea deciziei
    st.rerun()


def handle_reject(pair):
    # memoram respingerea pentru sesiunea curenta
    st.session_state.rejected_matches.add(pair)

    # ne asiguram ca aceeasi pereche nu este si acceptata
    st.session_state.accepted_matches.discard(pair)

    # rerulam dashboardul pentru aplicarea deciziei
    st.rerun()


def display_possible_matches(results):
    st.warning("⚠️ POSSIBLE MATCH")

    for invoice_number, data in results["possible_matches_by_invoice"].items():

        for payment in data["payments"]:

            pair = (
                invoice_number,
                payment["payment_id"],
            )

            match_key = f'{invoice_number}_{payment["payment_id"]}'

            col1, col2, col3, col4, col5, col6, col7 = st.columns(
                [1.3, 2, 2, 1.5, 1.2, 1, 1]
            )

            col1.write(invoice_number)
            col2.write(data["client"])
            col3.write(payment["name"])
            col4.write(payment["payment_date"])
            col5.write(f'{payment["amount"]:.2f} lei')

            if col6.button("✓", key=f"accept_{match_key}"):
                handle_accept(
                    pair,
                    payment,
                    data["client"],
                )

            if col7.button("✕", key=f"reject_{match_key}"):
                handle_reject(pair)


def display_unmatched(results):
    st.error("❌ FACTURI NEPLĂTITE")

    col1, col2, col3 = st.columns([1, 2, 1])

    col1.write("**Factură**")
    col2.write("**Client**")
    col3.write("**Sumă**")

    for invoice in results["unmatched"]:

        col1, col2, col3 = st.columns([1, 2, 1])

        col1.write(invoice["invoice_number"])
        col2.write(invoice["client"])
        col3.write(f'{invoice["amount"]:.2f} lei')


initialize_session_state()

st.title("Asociere facturi și plăți")

st.write("Încarcă fișierele pentru reconciliere.")

invoice_file = st.file_uploader(
    "Încarcă fișierul Excel cu facturi",
    type=["xlsx"],
)

payment_file = st.file_uploader(
    "Încarcă fișierul CSV cu plăți",
    type=["csv"],
)

if invoice_file is not None:
    st.write("Facturi:", invoice_file.name)

if payment_file is not None:
    st.write("Plăți:", payment_file.name)


process_button = st.button("Procesează")

if process_button:

    if invoice_file is not None and payment_file is not None:

        process_files(
            invoice_file,
            payment_file,
        )

    else:
        st.warning("Încarcă ambele fișiere înainte de procesare.")


if st.session_state.results is not None:

    apply_manual_decisions(
        st.session_state.results,
        st.session_state.invoices,
        st.session_state.accepted_matches,
        st.session_state.rejected_matches,
    )

    results = st.session_state.results

    pdf_buffer = generate_report_pdf(results)

    st.download_button(
        label="🖨️ Raport pentru print",
        data=pdf_buffer.getvalue(),
        file_name="raport_reconciliere.pdf",
        mime="application/pdf",
    )

    display_direct_matches(results)
    display_possible_matches(results)
    display_unmatched(results)
