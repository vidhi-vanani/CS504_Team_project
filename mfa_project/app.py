from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from routes import register, login, verify_user_face, verify_otp

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get JWT secret key from environment variables
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "default_secret_key_should_be_changed")

jwt = JWTManager(app)

# Register routes
app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])
app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/verify_face', 'verify_user_face', verify_user_face, methods=['POST'])
app.add_url_rule('/verify_otp', 'verify_otp', verify_otp, methods=['POST'])

if __name__ == "__main__":
    app.run(debug=True)
