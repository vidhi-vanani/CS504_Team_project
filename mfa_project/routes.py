from flask import request, jsonify, render_template, flash, redirect, url_for
from flask_jwt_extended import create_access_token
from models import create_user, find_user, verify_password, users
from utils import generate_email_otp, send_email, generate_qr
from face_auth import verify_face, register_face
import pyotp

# -------------------------
# 2FA Selection Page
# -------------------------
def choose_2fa():
    return render_template("choose_2fa.html")


# -------------------------
# Face Registration (POST)
# -------------------------
def register_user_face():
    data = request.get_json() if request.is_json else request.form
    try:
        username = data.get("username")
        success = register_face(username)
        if success:
            flash("Face registered successfully!", "success")
            return redirect(url_for("choose_2fa"))
        flash("Face registration failed!", "error")
        return redirect(url_for("choose_2fa"))
    except Exception as e:
        flash("Error: Missing or invalid username field", "error")
        return redirect(url_for("choose_2fa"))


# -------------------------
# User Registration (GET/POST)
# -------------------------
def register():
    if request.method == 'GET':
        return render_template('register.html')

    data = request.get_json() if request.is_json else request.form
    try:
        create_user(data["username"], data["email"], data["password"])
        secret, qr_path = generate_qr(data["username"])
        users.update_one({"username": data["username"]}, {"$set": {"totp_secret": secret}})
        if not request.is_json:
            return render_template('qr_code.html', qr_path=qr_path)
        return jsonify({"message": "User registered successfully", "qr_code": qr_path}), 201
    except KeyError:
        message = "Missing required fields"
        if request.is_json:
            return jsonify({"message": message}), 400
        flash(message, "error")
        return render_template('register.html')


# -------------------------
# User Login (GET/POST)
# -------------------------
def login():
    if request.method == 'GET':
        return render_template('login.html')

    data = request.get_json() if request.is_json else request.form
    try:
        user = find_user(data["username"])
        if user and verify_password(user["password_hash"], data["password"]):
            email_otp = generate_email_otp()
            send_email(user["email"], email_otp)
            users.update_one({"username": data["username"]}, {"$set": {"email_otp": email_otp}})
            return redirect(url_for('choose_2fa'))
        flash("Invalid credentials", "error")
        return render_template('login.html')
    except KeyError:
        flash("Missing required fields", "error")
        return render_template('login.html')


# -------------------------
# Face Verification (POST)
# -------------------------
def verify_user_face():
    data = request.get_json() if request.is_json else request.form
    try:
        username = data.get("username")
        if not username:
            flash("Username is required for face verification.", "error")
            return redirect(url_for("choose_2fa"))

        is_verified = verify_face(username)
        if is_verified:
            token = create_access_token(identity=username)
            return redirect(url_for("dashboard"))
        flash("Face not recognized", "error")
        return redirect(url_for("choose_2fa"))
    except:
        flash("Face verification failed", "error")
        return redirect(url_for("choose_2fa"))


# -------------------------
# Email OTP Verification
# -------------------------
def verify_otp():
    if request.method == "GET":
        return render_template("verify_otp.html")

    data = request.get_json() if request.is_json else request.form
    try:
        username = data.get("username")
        otp = str(data.get("otp")).strip()
        user = find_user(username)
        if not user:
            flash("User not found", "error")
            return redirect(url_for("choose_2fa"))

        if otp == str(user.get("email_otp")):
            users.update_one({"username": username}, {"$unset": {"email_otp": ""}})
            token = create_access_token(identity=username)
            return redirect(url_for("dashboard"))
        flash("Invalid Email OTP", "error")
        return redirect(url_for("choose_2fa"))
    except:
        flash("OTP verification failed", "error")
        return redirect(url_for("choose_2fa"))


# -------------------------
# TOTP (Authenticator App) Verification
# -------------------------
def verify_totp():
    if request.method == 'GET':
        return render_template("verify_totp.html")

    data = request.get_json() if request.is_json else request.form
    try:
        username = data.get("username")
        totp_code = str(data.get("totp")).strip()
        user = find_user(username)
        if not user or not user.get("totp_secret"):
            flash("User or TOTP not found", "error")
            return redirect(url_for("choose_2fa"))

        totp = pyotp.TOTP(user["totp_secret"])
        if totp.verify(totp_code):
            token = create_access_token(identity=username)
            return redirect(url_for("dashboard"))
        flash("Invalid Authenticator Code", "error")
        return redirect(url_for("choose_2fa"))
    except:
        flash("Verification failed", "error")
        return redirect(url_for("choose_2fa"))


# -------------------------
# Resend OTP to Email
# -------------------------
def resend_otp():
    username = request.args.get("username")
    if not username:
        flash("Username required to resend OTP", "error")
        return redirect(url_for("verify_otp"))

    user = find_user(username)
    if not user:
        flash("User not found", "error")
        return redirect(url_for("verify_otp"))

    new_otp = generate_email_otp()
    send_email(user["email"], new_otp)
    users.update_one({"username": username}, {"$set": {"email_otp": new_otp}})
    flash("A new OTP has been sent to your email.", "success")
    return redirect(url_for("verify_otp", username=username))
