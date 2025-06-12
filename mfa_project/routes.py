from flask import request, jsonify, render_template, flash, redirect, url_for
from flask_jwt_extended import create_access_token
from models import create_user, find_user, verify_password, users
from utils import generate_email_otp, send_email, generate_qr
from face_auth import verify_face
import pyotp

def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        try:
            # Create user and generate TOTP secret/QR code
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
            else:
                flash(message, "error")
                return render_template('register.html')

def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        try:
            user = find_user(data["username"])
            if user and verify_password(user["password_hash"], data["password"]):
                email_otp = generate_email_otp()
                send_email(user["email"], email_otp)
                users.update_one({"username": data["username"]}, {"$set": {"email_otp": email_otp}})
                if request.is_json:
                    return jsonify({"otp_sent": True, "message": "Check your email for OTP"}), 200
                else:
                    flash("Check your email for OTP", "success")
                    return redirect(url_for('verify_otp'))
            else:
                message = "Invalid credentials"
                if request.is_json:
                    return jsonify({"message": message}), 401
                else:
                    flash(message, "error")
                    return render_template('login.html')
        except KeyError:
            message = "Missing required fields"
            if request.is_json:
                return jsonify({"message": message}), 400
            else:
                flash(message, "error")
                return render_template('login.html')

def verify_user_face():
    data = request.get_json()
    try:
        username = data["username"]
        is_verified = verify_face(username)
        if is_verified:
            return jsonify({"message": "Face authentication successful!"}), 200
        return jsonify({"message": "Face authentication failed!"}), 401
    except KeyError:
        return jsonify({"message": "Missing username field"}), 400

def verify_otp():
    if request.method == "GET":
        return render_template("verify_otp.html")
    
    data = request.get_json() if request.is_json else request.form
    try:
        username = data.get("username")
        otp = str(data.get("otp")).strip()
        totp_code = str(data.get("totp")).strip()
        user = find_user(username)
        if not user:
            message = "User not found."
            if request.is_json:
                return jsonify({"message": message}), 404
            else:
                flash(message, "error")
                return render_template("verify_otp.html")

        # Email OTP verification
        email_otp_valid = otp == str(user.get("email_otp"))

        # Authenticator (TOTP) verification
        totp_secret = user.get("totp_secret")
        if not totp_secret:
            message = "Authenticator not set up for this user."
            if request.is_json:
                return jsonify({"message": message}), 400
            else:
                flash(message, "error")
                return render_template("verify_otp.html")
        totp = pyotp.TOTP(totp_secret)
        totp_valid = totp.verify(totp_code)

        if email_otp_valid and totp_valid:
            token = create_access_token(identity=username)
            users.update_one({"username": username}, {"$unset": {"email_otp": ""}})
            if request.is_json:
                return jsonify({"access_token": token}), 200
            else:
                flash("OTP and Authenticator code verified successfully!", "success")
                return redirect(url_for('dashboard'))
        else:
            if not email_otp_valid and not totp_valid:
                msg = "Both OTP and Authenticator code are invalid."
            elif not email_otp_valid:
                msg = "Invalid Email OTP."
            else:
                msg = "Invalid Authenticator code."
            if request.is_json:
                return jsonify({"message": msg}), 401
            else:
                flash(msg, "error")
                return render_template("verify_otp.html")
    except Exception:
        if request.is_json:
            return jsonify({"message": "Missing required fields or error occurred"}), 400
        else:
            flash("Missing required fields or error occurred", "error")
            return render_template("verify_otp.html")
