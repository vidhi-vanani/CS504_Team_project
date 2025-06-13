import os
from pymongo import MongoClient
from flask_bcrypt import Bcrypt

# MongoDB connection using secure environment variable fallback
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://tejasreekokkanti20:Dhanama123@506tp.evuyp7x.mongodb.net/?retryWrites=true&w=majority&appName=506TP")
client = MongoClient(MONGO_URI)
db = client["mfa_db"]
users = db["users"]

# Initialize bcrypt
bcrypt = Bcrypt()

# -----------------------------
# User Registration
# -----------------------------
def create_user(username, email, password):
    """
    Create a new user in the database with hashed password.
    Also prepares fields for MFA methods.
    """
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    users.insert_one({
        "username": username,
        "email": email,
        "password_hash": hashed_password,
        "totp_secret": None,
        "face_encoding": None,
        "email_otp": None
    })

# -----------------------------
# User Query
# -----------------------------
def find_user(username):
    """
    Find and return a user by username.
    """
    return users.find_one({"username": username})

# -----------------------------
# Password Verification
# -----------------------------
def verify_password(stored_hash, password):
    """
    Check whether the password entered matches the stored hash.
    """
    return bcrypt.check_password_hash(stored_hash, password)
