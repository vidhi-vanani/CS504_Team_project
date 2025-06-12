from pymongo import MongoClient
from flask_bcrypt import Bcrypt

# Use environment variable for MongoDB URI for security
import os
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://tejasreekokkanti20:Dhanama123@506tp.evuyp7x.mongodb.net/?retryWrites=true&w=majority&appName=506TP")

client = MongoClient(MONGO_URI)
db = client["mfa_db"]
users = db["users"]
bcrypt = Bcrypt()

def create_user(username, email, password):
    """Stores user credentials in MongoDB"""
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    users.insert_one({
        "username": username,
        "email": email,
        "password_hash": hashed_password,
        "totp_secret": None,
        "face_encoding": None,
        "email_otp": None  # Add this field for clarity
    })

def find_user(username):
    """Find user by username"""
    return users.find_one({"username": username})

def verify_password(stored_hash, password):
    """Check password validity"""
    return bcrypt.check_password_hash(stored_hash, password)
