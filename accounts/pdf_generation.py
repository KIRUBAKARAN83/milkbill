from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
from io import BytesIO
from decimal import Decimal


def generate_bill_pdf(
    customer,
    entries,
    total_ml,
    total_litres,
    total_amount,
    price_per_litre,
    year=None,
    month=None
):
    """
    RULE (FINAL):
    - customer.balance_amount = unpaid till previous month
    - total_amount = current month amount
    - total payable = previous balance + current month amount
    """

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=20,
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )

    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading3'],
        fontSize=11,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )

    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=4
    )

    elements = []

    # ---------------- TITLE ----------------
    elements.append(Paragraph("Milk Billing Invoice", title_style))

    if year and month:
        month_name = datetime(year, month, 1).strftime('%B %Y')
        period_text = f"Billing Period: {month_name}"
    else:
        period_text = "Billing Period: All Records"

    elements.append(
        Paragraph(
            f"{period_text}<br/>Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
            normal_style
        )
    )

    elements.append(Spacer(1, 0.2 * inch))

    # ---------------- CUSTOMER SUMMARY (FIXED LOGIC) ----------------
    previous_balance = Decimal(customer.balance_amount or 0)
    current_month_amount = Decimal(total_amount)
    total_payable = previous_balance + current_month_amount

    elements.append(Paragraph("Customer Summary", heading_style))

    summary_table = Table(
        [
            ["Customer Name", customer.name or "N/A"],
            ["Previous Balance (Unpaid)", f"₹ {previous_balance:.2f}"],
            ["Current Month Amount", f"₹ {current_month_amount:.2f}"],
            ["Total Payable", f"₹ {total_payable:.2f}"],
        ],
        colWidths=[3 * inch, 2 * inch]
    )

    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 0.25 * inch))

    # ---------------- ENTRIES TABLE ----------------
    elements.append(Paragraph("Milk Entries", heading_style))

    table_data = [
        ["Date", "Quantity (ml)", "Litres", "Rate (₹)", "Amount (₹)"]
    ]

    if entries:
        for entry in entries:
            table_data.append([
                entry.date.strftime('%d-%m-%Y'),
                str(entry.quantity_ml),
                f"{entry.litres:.3f}",
                f"{Decimal(price_per_litre):.2f}",
                f"{entry.amount:.2f}",
            ])
    else:
        table_data.append(["No entries", "", "", "", ""])

    table_data.append([
        "TOTAL (This Month)",
        str(total_ml),
        f"{total_litres:.2f}",
        f"{Decimal(price_per_litre):.2f}",
        f"{current_month_amount:.2f}",
    ])

    entries_table = Table(table_data, colWidths=[1.2 * inch] * 5)

    entries_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
    ]))

    elements.append(entries_table)
    elements.append(Spacer(1, 0.3 * inch))

    # ---------------- FOOTER ----------------
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.grey
    )

    elements.append(
        Paragraph("Thank you for your business.", footer_style)
    )

    doc.build(elements)
    buffer.seek(0)
    return buffer
