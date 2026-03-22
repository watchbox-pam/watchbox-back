import smtplib
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_mail(to: str, subject: str, content: str):

    smtp_server: str = os.getenv("SMTP_SERVER")
    smtp_port: int = int(os.getenv("SMTP_PORT")) | 587
    smtp_email: str = os.getenv("SMTP_EMAIL")
    smtp_password: str = os.getenv("SMTP_PASSWORD")

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["To"] = to
        msg["From"] = smtp_email
        msg_content = MIMEText(content, "html")
        msg.attach(msg_content)

        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)

    except Exception as e:
        print("SMTP ERROR:", repr(e))