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
    Generate PDF bill for customer
    Assumes `entries` already excludes soft-deleted rows
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

    # ✅ FIXED BLOCK
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

    # ---------------- CUSTOMER INFO ----------------
    elements.append(Paragraph("Customer Details", heading_style))

    cust_balance = customer.balance_amount or Decimal(0)

    cust_table = Table(
        [
            ["Name", customer.name or "N/A"],
            ["Current Balance", f"₹ {cust_balance:.2f}"],
        ],
        colWidths=[2 * inch, 3 * inch]
    )

    cust_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(cust_table)
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
        "TOTAL",
        str(total_ml),
        f"{total_litres:.2f}",
        f"{Decimal(price_per_litre):.2f}",
        f"{Decimal(total_amount):.2f}",
    ])

    entries_table = Table(
        table_data,
        colWidths=[1.2 * inch] * 5
    )

    entries_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
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

    elements.append(Paragraph("Thank you for your business.", footer_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
