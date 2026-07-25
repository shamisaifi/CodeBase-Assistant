import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config.settings import settings

def send_email(to: str, subject: str, html_body: str, text_body: str = None):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to

    if text_body:
        msg.attach(MIMEText(text_body, "plain"))
    
    msg.attach(MIMEText(html_body, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.sendmail(settings.SMTP_FROM, to, msg.as_string())


def send_otp_email(to: str, otp: str, username: str):
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px;">
        <h2>Password Reset OTP</h2>
        <p>Hi {username},</p>
        <p>Your OTP is:</p>
        <h1 style="color: #4F46E5; letter-spacing: 8px;">{otp}</h1>
        <p>Valid for <strong>10 minutes</strong>.</p>
        <p>If you didn't request this, ignore this email.</p>
    </div>
    """
    send_email(to, "Password Reset OTP", html)


def send_welcome_email(to: str, username: str):
    html = f"""
    <div style="font-family: Arial, sans-serif;">
        <h2>Welcome, {username}!</h2>
        <p>Your account has been created successfully.</p>
    </div>
    """
    send_email(to, "Welcome to Codebase Assistant", html)
