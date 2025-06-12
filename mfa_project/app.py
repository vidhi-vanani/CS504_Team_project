from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

from routes import register, login, verify_user_face, verify_otp

load_dotenv()

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "default_secret_key_should_be_changed")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "change_this_secret_key")

jwt = JWTManager(app)

# Register routes with GET and POST methods as needed
app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])
app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/verify_face', 'verify_user_face', verify_user_face, methods=['POST'])
app.add_url_rule('/verify-otp', 'verify_otp', verify_otp, methods=['GET', 'POST'])  # <-- hyphen

@app.route('/dashboard')
def dashboard():
    return "Welcome to your dashboard! You are logged in."

if __name__ == "__main__":
    app.run(debug=True)
