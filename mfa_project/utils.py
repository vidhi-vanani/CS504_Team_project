import os
import pyotp
import qrcode
import smtplib
import random
from email.mime.text import MIMEText


# -----------------------------
# OTP Generator
# -----------------------------
def generate_email_otp():
    """
    Generate a 4-digit numeric OTP for email verification.
    """
    return str(random.randint(1000, 9999))


# -----------------------------
# Email Sender for OTP
# -----------------------------
def send_email(to_email, otp):
    """
    Sends the OTP to the specified email using Gmail SMTP.
    Requires EMAIL_PASSWORD to be set as environment variable.
    """
    sender_email = "tejasreekokkanti20@gmail.com"
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_password:
        raise ValueError("EMAIL_PASSWORD environment variable not set!")

    msg = MIMEText(f"Your OTP code is: {otp}")
    msg["Subject"] = "Your MFA Authentication Code"
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
    except Exception as e:
        raise RuntimeError(f"Failed to send email: {e}")


# -----------------------------
# TOTP + QR Generator
# -----------------------------
def generate_qr(username):
    """
    Generates a TOTP secret for the user and creates a QR code image.
    Returns: secret key, path to QR code image
    """
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    qr_uri = totp.provisioning_uri(username, issuer_name="SecureAuth")

    qr = qrcode.make(qr_uri)

    qr_folder = "static"
    if not os.path.exists(qr_folder):
        os.makedirs(qr_folder)

    qr_path = os.path.join(qr_folder, f"{username}_qr.png")
    qr.save(qr_path)

    return secret, f"/{qr_path}"
