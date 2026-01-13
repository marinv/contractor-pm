import os
import base64
from io import BytesIO
from datetime import datetime
from sqlalchemy.orm import Session

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

from app.models.project import Project
from app.models.time_entry import TimeEntry
from app.models.material import Material
from app.models.worker_type import WorkerType

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")


def calculate_project_costs(project: Project, db: Session):
    # Calculate labor costs
    labor_costs = []
    total_labor = 0
    time_entries = db.query(TimeEntry).filter(TimeEntry.project_id == project.id).all()

    worker_hours = {}
    for entry in time_entries:
        worker_type = db.query(WorkerType).filter(WorkerType.id == entry.worker_type_id).first()
        if worker_type:
            key = worker_type.id
            if key not in worker_hours:
                worker_hours[key] = {
                    "name": worker_type.name,
                    "rate": worker_type.hourly_rate,
                    "hours": 0
                }
            worker_hours[key]["hours"] += entry.hours

    for wt in worker_hours.values():
        cost = wt["hours"] * wt["rate"]
        total_labor += cost
        labor_costs.append({
            "worker_type": wt["name"],
            "hours": wt["hours"],
            "rate": wt["rate"],
            "cost": cost
        })

    # Calculate material costs
    material_costs = []
    total_materials = 0
    materials = db.query(Material).filter(Material.project_id == project.id).all()

    for mat in materials:
        cost = mat.quantity * mat.unit_price
        total_materials += cost
        material_costs.append({
            "name": mat.name,
            "quantity": mat.quantity,
            "unit": mat.unit,
            "unit_price": mat.unit_price,
            "cost": cost
        })

    return {
        "labor_costs": labor_costs,
        "material_costs": material_costs,
        "total_labor": total_labor,
        "total_materials": total_materials,
        "grand_total": total_labor + total_materials
    }


def get_logo_base64(logo_path: str) -> str:
    """Get logo as base64 string for HTML embedding."""
    if not logo_path:
        return None
    filepath = os.path.join(UPLOAD_DIR, logo_path)
    if not os.path.exists(filepath):
        return None
    with open(filepath, "rb") as f:
        data = f.read()
    ext = logo_path.split(".")[-1].lower()
    mime_type = f"image/{ext}" if ext in ["png", "jpg", "jpeg", "gif"] else "image/png"
    return f"data:{mime_type};base64,{base64.b64encode(data).decode()}"


def generate_html_report(project: Project, db: Session, company_name: str, logo_path: str = None) -> str:
    costs = calculate_project_costs(project, db)
    logo_base64 = get_logo_base64(logo_path)

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Commercial Offer - {project.name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #2c5282;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .company-name {{
            font-size: 24px;
            font-weight: bold;
            color: #2c5282;
        }}
        .company-logo {{
            max-height: 80px;
            max-width: 200px;
            margin-bottom: 10px;
        }}
        .document-title {{
            font-size: 20px;
            color: #666;
            margin-top: 10px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section-title {{
            font-size: 16px;
            font-weight: bold;
            color: #2c5282;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
            margin-bottom: 15px;
        }}
        .info-row {{
            display: flex;
            margin-bottom: 8px;
        }}
        .info-label {{
            font-weight: bold;
            width: 150px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }}
        th {{
            background-color: #f5f5f5;
            font-weight: bold;
        }}
        .text-right {{
            text-align: right;
        }}
        .total-row {{
            font-weight: bold;
            background-color: #f9f9f9;
        }}
        .grand-total {{
            font-size: 18px;
            font-weight: bold;
            text-align: right;
            margin-top: 20px;
            padding: 15px;
            background-color: #2c5282;
            color: white;
        }}
        .offer-terms {{
            margin-top: 30px;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 4px;
        }}
        .terms-content {{
            white-space: pre-wrap;
            line-height: 1.6;
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        {f'<img src="{logo_base64}" class="company-logo" alt="Company Logo" />' if logo_base64 else ''}
        <div class="company-name">{company_name or 'Contractor Services'}</div>
        <div class="document-title">Commercial Offer</div>
    </div>

    <div class="section">
        <div class="section-title">Project Information</div>
        <div class="info-row">
            <span class="info-label">Project Name:</span>
            <span>{project.name}</span>
        </div>
        <div class="info-row">
            <span class="info-label">Description:</span>
            <span>{project.description or 'N/A'}</span>
        </div>
        <div class="info-row">
            <span class="info-label">Date:</span>
            <span>{datetime.now().strftime('%Y-%m-%d')}</span>
        </div>
    </div>

    <div class="section">
        <div class="section-title">Customer Information</div>
        <div class="info-row">
            <span class="info-label">Name:</span>
            <span>{project.customer_name or 'N/A'}</span>
        </div>
        <div class="info-row">
            <span class="info-label">Email:</span>
            <span>{project.customer_email or 'N/A'}</span>
        </div>
        <div class="info-row">
            <span class="info-label">Address:</span>
            <span>{project.customer_address or 'N/A'}</span>
        </div>
    </div>

    <div class="section">
        <div class="section-title">Labor Costs</div>
        <table>
            <thead>
                <tr>
                    <th>Worker Type</th>
                    <th class="text-right">Hours</th>
                    <th class="text-right">Rate (€/hr)</th>
                    <th class="text-right">Cost (€)</th>
                </tr>
            </thead>
            <tbody>
"""

    for item in costs["labor_costs"]:
        html += f"""
                <tr>
                    <td>{item['worker_type']}</td>
                    <td class="text-right">{item['hours']:.1f}</td>
                    <td class="text-right">{item['rate']:.2f}</td>
                    <td class="text-right">{item['cost']:.2f}</td>
                </tr>
"""

    html += f"""
                <tr class="total-row">
                    <td colspan="3">Subtotal Labor</td>
                    <td class="text-right">€{costs['total_labor']:.2f}</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="section">
        <div class="section-title">Material Costs</div>
        <table>
            <thead>
                <tr>
                    <th>Material</th>
                    <th class="text-right">Quantity</th>
                    <th>Unit</th>
                    <th class="text-right">Unit Price (€)</th>
                    <th class="text-right">Cost (€)</th>
                </tr>
            </thead>
            <tbody>
"""

    for item in costs["material_costs"]:
        html += f"""
                <tr>
                    <td>{item['name']}</td>
                    <td class="text-right">{item['quantity']:.1f}</td>
                    <td>{item['unit']}</td>
                    <td class="text-right">{item['unit_price']:.2f}</td>
                    <td class="text-right">{item['cost']:.2f}</td>
                </tr>
"""

    html += f"""
                <tr class="total-row">
                    <td colspan="4">Subtotal Materials</td>
                    <td class="text-right">€{costs['total_materials']:.2f}</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="grand-total">
        Grand Total: €{costs['grand_total']:.2f}
    </div>

    {f'<div class="offer-terms"><div class="section-title">Terms and Conditions</div><div class="terms-content">{project.offer_terms.replace(chr(10), "<br/>")}</div></div>' if project.offer_terms else ''}

    <div class="footer">
        <p>This offer is valid for 30 days from the date of issue.</p>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
</body>
</html>
"""
    return html


def generate_pdf_report(project: Project, db: Session, company_name: str, logo_path: str = None) -> BytesIO:
    costs = calculate_project_costs(project, db)
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2c5282'),
        alignment=1,
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.grey,
        alignment=1,
        spaceAfter=30
    )
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c5282'),
        spaceAfter=10,
        spaceBefore=20
    )

    elements = []

    # Logo
    if logo_path:
        logo_filepath = os.path.join(UPLOAD_DIR, logo_path)
        if os.path.exists(logo_filepath):
            try:
                logo = Image(logo_filepath)
                # Scale logo to fit (max 4cm height, max 6cm width)
                logo_width = logo.drawWidth
                logo_height = logo.drawHeight
                max_width = 6 * cm
                max_height = 4 * cm

                scale_w = max_width / logo_width if logo_width > max_width else 1
                scale_h = max_height / logo_height if logo_height > max_height else 1
                scale = min(scale_w, scale_h)

                logo.drawWidth = logo_width * scale
                logo.drawHeight = logo_height * scale
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 10))
            except Exception:
                pass  # Skip logo if there's an error loading it

    # Header
    elements.append(Paragraph(company_name or "Contractor Services", title_style))
    elements.append(Paragraph("Commercial Offer", subtitle_style))

    # Project Information
    elements.append(Paragraph("Project Information", section_style))
    project_data = [
        ["Project Name:", project.name],
        ["Description:", project.description or "N/A"],
        ["Date:", datetime.now().strftime('%Y-%m-%d')],
    ]
    t = Table(project_data, colWidths=[4*cm, 12*cm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(t)

    # Customer Information
    elements.append(Paragraph("Customer Information", section_style))
    customer_data = [
        ["Name:", project.customer_name or "N/A"],
        ["Email:", project.customer_email or "N/A"],
        ["Address:", project.customer_address or "N/A"],
    ]
    t = Table(customer_data, colWidths=[4*cm, 12*cm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(t)

    # Labor Costs
    elements.append(Paragraph("Labor Costs", section_style))
    labor_data = [["Worker Type", "Hours", "Rate (€/hr)", "Cost (€)"]]
    for item in costs["labor_costs"]:
        labor_data.append([
            item['worker_type'],
            f"{item['hours']:.1f}",
            f"{item['rate']:.2f}",
            f"{item['cost']:.2f}"
        ])
    labor_data.append(["Subtotal Labor", "", "", f"€{costs['total_labor']:.2f}"])

    t = Table(labor_data, colWidths=[6*cm, 3*cm, 3.5*cm, 3.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f9f9f9')),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(t)

    # Material Costs
    elements.append(Paragraph("Material Costs", section_style))
    material_data = [["Material", "Qty", "Unit", "Unit Price (€)", "Cost (€)"]]
    for item in costs["material_costs"]:
        material_data.append([
            item['name'],
            f"{item['quantity']:.1f}",
            item['unit'],
            f"{item['unit_price']:.2f}",
            f"{item['cost']:.2f}"
        ])
    material_data.append(["Subtotal Materials", "", "", "", f"€{costs['total_materials']:.2f}"])

    t = Table(material_data, colWidths=[5*cm, 2*cm, 2*cm, 3.5*cm, 3.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f9f9f9')),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(t)

    # Grand Total
    elements.append(Spacer(1, 20))
    total_data = [[f"Grand Total: €{costs['grand_total']:.2f}"]]
    t = Table(total_data, colWidths=[16*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
    ]))
    elements.append(t)

    # Offer Terms
    if project.offer_terms:
        elements.append(Paragraph("Terms and Conditions", section_style))
        terms_style = ParagraphStyle(
            'Terms',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
            leading=14
        )
        # Split by newlines and create paragraphs
        for line in project.offer_terms.split('\n'):
            if line.strip():
                elements.append(Paragraph(line, terms_style))
            else:
                elements.append(Spacer(1, 6))

    # Footer
    elements.append(Spacer(1, 40))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=1
    )
    elements.append(Paragraph("This offer is valid for 30 days from the date of issue.", footer_style))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", footer_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
