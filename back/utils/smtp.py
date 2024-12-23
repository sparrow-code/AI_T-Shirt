import smtplib
from email.message import EmailMessage
from typing import List
from fastapi import HTTPException
from const import *

class SMTPController:
    def __init__(self, email_address: str, email_password: str):
        self.email_address = email_address
        self.email_password = email_password
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 465  # SSL Port
        self.server = None

    def start_session(self):
        """ Start SMTP session and login to the server """
        if self.server is None:
            self.server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            self.server.login(self.email_address, self.email_password)
            print("Logged in to the SMTP server.")

    def send_email(self, subject: str, body: str, recipients: List[str]):
        """ Send email using the existing SMTP session """
        if not self.server:
            raise HTTPException(status_code=500, detail="SMTP session not started")

        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = self.email_address
        msg['To'] = ', '.join(recipients)

        try:
            self.server.send_message(msg)
            print(f"Email sent successfully to {recipients}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    def close_session(self):
        """ Close the SMTP session gracefully """
        if self.server:
            self.server.quit()
            self.server = None
            print("SMTP session closed.")

# Create the SMTP controller instance
smtp_utils = SMTPController(email_address='your-email@gmail.com', email_password='your-email-password')
