from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.utils.security import get_current_user
from app.services.report_generator import generate_html_report, generate_pdf_report
from app.services.email_service import send_offer_email

router = APIRouter(prefix="/api/projects", tags=["reports"])


class SendEmailRequest(BaseModel):
    to_email: EmailStr
    subject: Optional[str] = None
    message: Optional[str] = None


@router.get("/{project_id}/report")
def get_report(
    project_id: int,
    format: str = "html",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    if format == "pdf":
        pdf_buffer = generate_pdf_report(project, db, current_user.company_name, current_user.logo_path, current_user.vat_id)
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=offer_{project.name.replace(' ', '_')}.pdf"
            }
        )
    else:
        html_content = generate_html_report(project, db, current_user.company_name, current_user.logo_path, current_user.vat_id)
        return HTMLResponse(content=html_content)


@router.post("/{project_id}/send-email")
def send_offer_by_email(
    project_id: int,
    email_data: SendEmailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Generate PDF
    pdf_buffer = generate_pdf_report(project, db, current_user.company_name, current_user.logo_path, current_user.vat_id)
    pdf_filename = f"offer_{project.name.replace(' ', '_')}.pdf"

    # Prepare email content
    company_name = current_user.company_name or "Contractor Services"
    subject = email_data.subject or f"Commercial Offer - {project.name} from {company_name}"

    default_message = f"""
    <html>
    <body>
    <p>Dear {project.customer_name or 'Customer'},</p>
    <p>Please find attached our commercial offer for the project: <strong>{project.name}</strong>.</p>
    <p>If you have any questions, please don't hesitate to contact us.</p>
    <p>Best regards,<br>{company_name}</p>
    </body>
    </html>
    """
    body = email_data.message or default_message

    # Send email with user in CC
    try:
        send_offer_email(
            to_email=email_data.to_email,
            cc_email=current_user.email,
            subject=subject,
            body=body,
            pdf_buffer=pdf_buffer,
            pdf_filename=pdf_filename
        )
        return {"message": f"Email sent successfully to {email_data.to_email}"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
