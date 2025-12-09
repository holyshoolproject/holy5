# utils/receipts.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from datetime import datetime


def build_payment_receipt(payment, stream, small_on_a4=True):
    FONT = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"

    c = canvas.Canvas(stream, pagesize=A4)
    width, height = A4

    # Simple top-left positioning (no centering, no fancy layout)
    x = 20 * mm
    y = height - 20 * mm

    # Header
    c.setFont(FONT_BOLD, 14)
    c.setFillColor(colors.HexColor("#0D6EFD"))
    c.drawString(x, y, "HOLYWELL INTERNATIONAL SCHOOL")
    y -= 10 * mm

    c.setFont(FONT_BOLD, 12)
    c.setFillColor(colors.HexColor("#1A365D"))
    c.drawString(x, y, "PAYMENT RECEIPT")
    y -= 12 * mm

    # Amount
    c.setFont(FONT_BOLD, 16)
    c.setFillColor(colors.HexColor("#198754"))
    c.drawString(x, y, f"Amount: GHS {float(payment.amount):,.2f}")
    y -= 12 * mm

    # Info section
    fr = payment.student_fee_record

    paid_status = "Full Payment" if fr.is_fully_paid else "Part Payment"

    info = [
        ("Student", fr.student.user.full_name),
        ("Status", paid_status),
        ("Payment ID", f"#{payment.pk:08d}"),
        ("Date", payment.date.strftime('%d %b %Y')),
        
        ("Class", f"{fr.fee_structure.grade_class}"),
        ("Term", f"{fr.fee_structure.term}"),
        ("Balance", f"GHS {float(fr.balance):,.2f}")
    ]

    c.setFont(FONT, 10)
    for label, value in info:
        c.setFillColor(colors.HexColor("#4A5568"))
        c.drawString(x, y, f"{label}:")
        c.setFillColor(colors.HexColor("#1A365D"))
        c.drawString(x + 30 * mm, y, str(value))
        y -= 7 * mm

    # Footer
    c.setFillColor(colors.HexColor("#A0AEC0"))
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(
        x,
        y - 10 * mm,
        f"Generated on {datetime.now().strftime('%d %b %Y, %I:%M %p')}"
    )

    c.showPage()
    c.save()
