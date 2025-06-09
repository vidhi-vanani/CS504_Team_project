from flask import request, jsonify, render_template
from flask_jwt_extended import create_access_token
from models import create_user, find_user, verify_password, users
from utils import generate_email_otp, send_email, generate_qr
from face_auth import verify_face  # updated import

def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        if request.is_json:
            data = request.json
        else:
            data = request.form
        try:
            create_user(data["username"], data["email"], data["password"])
            secret, qr_path = generate_qr(data["username"])
            users.update_one({"username": data["username"]}, {"$set": {"totp_secret": secret}})
            if not request.is_json:
                return render_template('qr_code.html', qr_path=qr_path)
            return jsonify({"message": "User registered successfully", "qr_code": qr_path}), 201
        except KeyError:
            return jsonify({"message": "Missing required fields"}), 400

def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        if request.is_json:
            data = request.json
        else:
            data = request.form
        try:
            user = find_user(data["username"])
            if user and verify_password(user["password_hash"], data["password"]):
                email_otp = generate_email_otp()
                send_email(user["email"], email_otp)
                users.update_one({"username": data["username"]}, {"$set": {"email_otp": email_otp}})
                return jsonify({"otp_sent": True, "message": "Check your email for OTP"}), 200
            return jsonify({"message": "Invalid credentials"}), 401
        except KeyError:
            return jsonify({"message": "Missing required fields"}), 400

def verify_user_face():
    data = request.json
    try:
        username = data["username"]
        is_verified = verify_face(username)
        if is_verified:
            return jsonify({"message": "Face authentication successful!"}), 200
        return jsonify({"message": "Face authentication failed!"}), 401
    except KeyError:
        return jsonify({"message": "Missing username field"}), 400

def verify_otp():
    data = request.json
    try:
        user = find_user(data["username"])
        if user and data["otp"] == user.get("email_otp"):
            token = create_access_token(identity=data["username"])
            users.update_one({"username": data["username"]}, {"$unset": {"email_otp": ""}})
            return jsonify({"access_token": token}), 200
        return jsonify({"message": "Invalid OTP"}), 401
    except KeyError:
        return jsonify({"message": "Missing required fields"}), 400
