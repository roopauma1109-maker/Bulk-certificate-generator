from pathlib import Path
import re
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas

OUTPUT_DIR = Path(__file__).resolve().parent / "generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip()).strip("_")
    return cleaned[:60] or "recipient"

def generate_certificate(certificate_id: int, recipient_name: str,
                         event_name: str, issuer: str, certificate_date: str) -> str:
    """Generate one PDF and return its absolute path."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"certificate_{certificate_id}_{safe_filename(recipient_name)}.pdf"
    page = landscape(A4)
    pdf = canvas.Canvas(str(path), pagesize=page)
    width, height = page

    pdf.setFillColor(colors.HexColor("#F8FAFC"))
    pdf.rect(0, 0, width, height, fill=1, stroke=0)
    pdf.setStrokeColor(colors.HexColor("#1D4ED8"))
    pdf.setLineWidth(5)
    pdf.rect(22, 22, width - 44, height - 44, fill=0, stroke=1)
    pdf.setFillColor(colors.HexColor("#1E3A8A"))
    pdf.setFont("Helvetica-Bold", 30)
    pdf.drawCentredString(width / 2, height - 105, "CERTIFICATE OF ACHIEVEMENT")
    pdf.setFillColor(colors.HexColor("#334155"))
    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(width / 2, height - 155, "This certificate is proudly presented to")
    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(width / 2, height - 205, recipient_name[:80])
    pdf.setFillColor(colors.HexColor("#334155"))
    pdf.setFont("Helvetica", 15)
    pdf.drawCentredString(width / 2, height - 250, f"For participating in: {event_name[:100]}")
    pdf.setFont("Helvetica", 13)
    pdf.drawCentredString(width / 2, 105, f"Issued by: {issuer[:100]}")
    pdf.drawCentredString(width / 2, 78, f"Date: {certificate_date[:40]}")
    pdf.save()
    return str(path)
