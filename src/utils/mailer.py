import os
import smtplib
from email.message import EmailMessage
from typing import Dict, Any

class SMTPMailer:
    def __init__(self):
        self.host = os.getenv("SMTP_HOST", "")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.user = os.getenv("SMTP_USER", "")
        self.password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("SMTP_FROM_EMAIL", self.user)

    def is_configured(self) -> bool:
        return bool(self.host and self.user and self.password)

    def send_email(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        if not self.is_configured():
            return {"success": False, "error": "SMTP credentials are not configured in .env"}

        try:
            msg = EmailMessage()
            msg.set_content(body)
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = recipient

            # Connect to SMTP server
            if self.port == 465:
                # SSL
                server = smtplib.SMTP_SSL(self.host, self.port)
            else:
                # TLS
                server = smtplib.SMTP(self.host, self.port)
                server.starttls()
            
            server.login(self.user, self.password)
            server.send_message(msg)
            server.quit()
            
            return {"success": True, "message": "Email sent successfully!"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to send email: {str(e)}"}
