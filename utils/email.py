from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
from typing import Optional

from fastapi import HTTPException


class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL")
        self.app_url = os.getenv("APP_URL", "http://localhost:8000")

    def send_verification_email(self, email: str, verification_token: str) -> None:
        """
        Send email verification link to user.

        Args:
            email: User's email address
            verification_token: Email verification token
        """
        if not all([self.smtp_username, self.smtp_password, self.from_email]):
            raise HTTPException(
                status_code=500,
                detail="Email configuration is incomplete",
            )

        verification_link = f"{self.app_url}/auth/verify-email/{verification_token}"

        message = MIMEMultipart()
        message["From"] = self.from_email
        message["To"] = email
        message["Subject"] = "Verify your email address"

        body = f"""
        <html>
            <body>
                <h2>Welcome to IfiaSoft!</h2>
                <p>Please click the link below to verify your email address:</p>
                <p><a href="{verification_link}">Verify Email</a></p>
                <p>If you did not create an account, please ignore this email.</p>
            </body>
        </html>
        """

        message.attach(MIMEText(body, "html"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send verification email: {str(e)}",
            )


email_service = EmailService()
