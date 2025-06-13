from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

# Import route handlers
from routes import (
    choose_2fa,
    verify_totp,
    register,
    login,
    verify_user_face,
    verify_otp,
    register_user_face,
    resend_otp  # <-- Added here
)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Secret keys for JWT and session
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "default_secret_key_should_be_changed")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "change_this_secret_key")

# Initialize JWT
jwt = JWTManager(app)

# --- API Route registrations ---
app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])
app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/choose-2fa', 'choose_2fa', choose_2fa, methods=['GET'])
app.add_url_rule('/verify-otp', 'verify_otp', verify_otp, methods=['GET', 'POST'])
app.add_url_rule('/verify-totp', 'verify_totp', verify_totp, methods=['GET', 'POST'])
app.add_url_rule('/verify_face', 'verify_user_face', verify_user_face, methods=['POST'])
app.add_url_rule('/register-face', 'register_user_face', register_user_face, methods=['POST'])
app.add_url_rule('/resend-otp', 'resend_otp', resend_otp, methods=['GET'])  # <-- Newly added route

# --- Optional rendering routes for face registration/verification forms ---
@app.route('/register-face-form')
def register_face_form():
    return render_template("register_face.html")

@app.route('/verify-face-form')
def verify_face_form():
    return render_template("verify_face.html")

# --- Dashboard ---
@app.route('/dashboard')
def dashboard():
    return "Welcome to your dashboard! You are logged in."

# --- App entry point ---
if __name__ == "__main__":
    app.run(debug=True)
