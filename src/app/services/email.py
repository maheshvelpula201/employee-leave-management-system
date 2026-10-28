# src/app/services/email.py

import os
import smtplib
from email.message import EmailMessage
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Thread pool for non-blocking asynchronous email dispatch
_email_executor = ThreadPoolExecutor(max_workers=2)

def _send_sync_email(to_email: str, subject: str, body: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("EMAILS_FROM_EMAIL", smtp_user or "noreply@peoplesphere.local")

    if not smtp_host or not smtp_user or not smtp_password:
        logger.warning("SMTP credentials not fully configured. Skipping email dispatch to %s", to_email)
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(body)

    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10) as server:
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        logger.info("Successfully sent email to %s", to_email)
    except Exception as e:
        logger.error("Failed to send email to %s: %s", to_email, str(e))

def send_invitation_email_async(to_email: str, invite_url: str, role: str, company_name: str = "Your Company"):
    """
    Sends an invitation email asynchronously using a thread pool executor
    so that HTTP response creation is not blocked by SMTP network IO.
    """
    if not to_email:
        return

    subject = f"You have been invited to join {company_name} as {role}"
    body = (
        f"Hello,\n\n"
        f"You have been invited to join {company_name} as a {role}.\n\n"
        f"Click the link below to accept your invitation and create your account:\n"
        f"{invite_url}\n\n"
        f"This invitation link will expire according to the administrator's settings.\n"
        f"If you did not expect this invitation, please ignore this email.\n"
    )

    _email_executor.submit(_send_sync_email, to_email, subject, body)