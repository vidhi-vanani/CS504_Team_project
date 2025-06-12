import pyotp
import qrcode
import smtplib
from email.mime.text import MIMEText
import random
import os

def generate_email_otp():
    """Generate a 4-digit numeric OTP"""
    return str(random.randint(1000, 9999))

def send_email(to_email, otp):
    """Send OTP via Email"""
    sender_email = "tejasreekokkanti20@gmail.com"
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_password:
        raise ValueError("EMAIL_PASSWORD environment variable not set!")

    msg = MIMEText(f"Your OTP code is: {otp}")
    msg["Subject"] = "Your MFA Authentication Code"
    msg["From"] = sender_email
    msg["To"] = to_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())

def generate_qr(username):
    """Generate a TOTP secret & QR Code"""
    secret = pyotp.random_base32()  # generate once per user
    totp = pyotp.TOTP(secret)
    qr_uri = totp.provisioning_uri(username, issuer_name="SecureAuth")
    qr = qrcode.make(qr_uri)
    qr.save(f"static/{username}_qr.png")
    return secret, f"/static/{username}_qr.png"
