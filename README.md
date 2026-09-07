# Invoice Reconciliation

A Python application for automatically reconciling invoices with bank payments.

The project imports invoice data from Excel files and payment data from CSV bank statements, then attempts to match payments with invoices based on multiple business rules.

The application also provides an interactive Streamlit dashboard where ambiguous matches can be manually accepted or rejected.

## Features

- Import invoices from Excel files
- Import bank payments from CSV files
- Automatic invoice-payment reconciliation
- Exact invoice number matching
- Client and payer name comparison
- Payment amount validation
- Invoice and payment month validation
- Detection of possible matches
- Manual Accept / Reject decisions
- Persistent payer-client relationships
- Identification of unpaid invoices
- PDF reconciliation reports
- Interactive Streamlit dashboard
- Automated tests with pytest

## Matching Logic

The reconciliation process classifies invoices into three main categories:

### Direct Matches

A payment is considered a direct match when:

- the payment amount matches the invoice amount
- the invoice and payment belong to the same month
- and either:
  - the invoice number is found in the payment description
  - the payer name exactly matches the invoice client
  - a previously confirmed payer-client relationship exists

### Possible Matches

A payment can be classified as a possible match when:

- the amount matches
- the payer and client names have common elements
- the payment belongs to the same month or references the invoice month in the payment description

Possible matches can be manually reviewed from the dashboard.

### Unpaid Invoices

Invoices for which no valid payment match is found are classified as unpaid.

## Manual Decisions

The Streamlit dashboard allows the user to:

- accept a possible match
- reject a possible match
- automatically move accepted matches to Direct Matches
- move invoices with no remaining candidates to Unpaid Invoices

Confirmed payer-client relationships are stored and reused during future reconciliations.

Example:

Invoice client: Popescu Ana
Payment payer: Popescu Ion
If the relationship is manually confirmed once, future payments from Popescu Ion can automatically match invoices belonging to Popescu Ana, provided the other reconciliation conditions are satisfied.


# Technologies:
Python
Streamlit
openpyxl
pytest
ReportLab
CSV
JSON

# Project structure:
invoice-reconciliation/
│
├── dashboard.py
├── imports.py
├── main.py
├── manual_decisions.py
├── reconciliation.py
├── relations.py
├── report.py
│
├── tests/
│   ├── test_manual_decisions.py
│   ├── test_reconciliation.py
│   └── test_relations.py
│
└── README.md

# Running the Application:
Activate the virtual environment and run:
 - streamlit run dashboard.py
The dashboard allows the user to upload:
 - an Excel file containing invoices
 - a CSV file containing bank payments
The reconciliation process is then executed automatically.

# Testing:
The project includes automated tests using pytest.
Run the tests with:
 - python -m pytest

# Data Privacy:
Real invoice and bank payment data are excluded from the repository.
The data/ directory and other sensitive files are ignored using .gitignore.

# Project Purpose:
This project was developed as a practical Python application for solving a real-world invoice reconciliation problem.
The goal was to automate a previously manual process while still allowing human validation for ambiguous cases.
