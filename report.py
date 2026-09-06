from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet


def apply_table_style(table):
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )


def generate_report_pdf(results):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
    )
    # creez datele din pdf
    elements = []
    styles = getSampleStyleSheet()
    elements.append(
        Paragraph(
            "Raport reconciliere facturi si plati",
            styles["Title"],
        )
    )
    elements.append(Spacer(1, 20))
    elements.append(
        Paragraph(
            "Facturi platite",
            styles["Heading2"],
        )
    )
    elements.append(Spacer(1, 10))
    direct_data = [
        [
            "Factura",
            "Client",
            "Platitor",
            "Data platii",
            "Suma",
        ]
    ]
    for match in sorted(
        results["direct_matches"],
        key=lambda match: match["invoice_number"],
    ):
        direct_data.append(
            [
                match["invoice_number"],
                match["client"],
                match["payer_name"],
                match["payment_date"],
                f'{match["amount"]:.2f} lei',
            ]
        )

    direct_table = Table(direct_data)
    apply_table_style(direct_table)
    elements.append(direct_table)

    elements.append(Spacer(1, 20))
    elements.append(
        Paragraph(
            "Facturi neplatite",
            styles["Heading2"],
        )
    )
    elements.append(Spacer(1, 10))
    unmatched_data = [
        [
            "Factura",
            "Client",
            "Suma",
        ]
    ]
    for invoice in sorted(
        results["unmatched"],
        key=lambda invoice: invoice["invoice_number"],
    ):
        unmatched_data.append(
            [
                invoice["invoice_number"],
                invoice["client"],
                f'{invoice["amount"]:.2f} lei',
            ]
        )

    unmatched_table = Table(unmatched_data)
    apply_table_style(unmatched_table)
    elements.append(unmatched_table)

    # face pdful cu datele pe care i le am dat eu
    doc.build(elements)
    buffer.seek(0)

    return buffer
