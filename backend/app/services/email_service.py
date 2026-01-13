import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from io import BytesIO

from app.config import settings


def send_offer_email(
    to_email: str,
    cc_email: str,
    subject: str,
    body: str,
    pdf_buffer: BytesIO,
    pdf_filename: str
) -> bool:
    """Send an email with PDF attachment."""

    if not settings.SMTP_HOST or not settings.SMTP_USER:
        raise ValueError("Email settings not configured. Please set SMTP_HOST, SMTP_USER, SMTP_PASSWORD in .env file")

    msg = MIMEMultipart()
    msg['From'] = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
    msg['To'] = to_email
    msg['Cc'] = cc_email
    msg['Subject'] = subject

    # Email body
    msg.attach(MIMEText(body, 'html'))

    # Attach PDF
    pdf_buffer.seek(0)
    pdf_attachment = MIMEApplication(pdf_buffer.read(), _subtype='pdf')
    pdf_attachment.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
    msg.attach(pdf_attachment)

    # Send email
    recipients = [to_email]
    if cc_email:
        recipients.append(cc_email)

    try:
        if settings.SMTP_USE_TLS:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)

        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, recipients, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")
