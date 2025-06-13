import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    
    # MongoDB Settings
    MONGO_URI = "mongodb+srv://tejasreekokkanti20:Dhanama123@506tp.evuyp7x.mongodb.net/?retryWrites=true&w=majority&appName=506TP"
    
    # Email Settings
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "tejsreekokkanti20@gmail.com"
    MAIL_PASSWORD = "Dhanama@123"
