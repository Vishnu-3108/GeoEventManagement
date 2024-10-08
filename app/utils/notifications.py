from fastapi import BackgroundTasks
from typing import Optional
from app.database import users_collection, events_collection
import smtplib
from email.mime.text import MIMEText

def send_email(to_email: str, subject: str, body: str):
    # Configure your SMTP server details
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "your_email@gmail.com"
    smtp_password = "your_email_password"
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_username
    msg["To"] = to_email
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)

async def notify_user(email: str, subject: str, message: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email, subject, message)
