# CS504_Team_project

# Multi-Factor Authentication (MFA) Web App
 
A lightweight and secure Multi-Factor Authentication system built using **Flask** and **MongoDB**, supporting two MFA methods:
 
- **Email OTP** (One-Time Password sent to user email)
- **TOTP with QR Code** (compatible with Google Authenticator / Authy)
 
This app allows users to register with a username, password, PIN, and email address, and securely log in using multiple authentication factors.
 
---
 
## Tech Stack
 
| Component         | Technology                           |
|------------------|---------------------------------------|
| Backend           | Flask (Python)                        |
| Database          | MongoDB with pymongo                  |
| Security          | bcrypt (password hashing)             |
| OTP Generation    | pyotp (TOTP), Email OTP via Flask-Mail|
| QR Code Support   | qrcode + PIL                          |
| Email Service     | SMTP (Gmail or others)                |
| Frontend          | HTML (Jinja2 templates)               |
 
---
 
## Project Structure
```
mfa_project/
├── app.py # Main Flask application
├── config.py # Email, MongoDB, and Flask configuration
├── models.py # MongoDB connection and user collection
├── requirements.txt # All Python dependencies
├── templates/
│ ├── register.html # Registration form
│ ├── login.html # Login form
│ ├── mfa.html # MFA page for OTP verification
│ └── home.html # Protected page after login
└── static/ # (Optional CSS/JS)
 ```
 
---
 
## Setup Instructions
 
### Clone the Repository
 
```bash
git clone https://github.com/your-username/mfa-flask.git
cd mfa-project
```
 
### Create a Virtual Environment & Install Dependencies

python -m venv venv
source venv/bin/activate          # On Windows: venv\Scripts\activate
```pip install -r requirements.txt```

---
### Install All Dependencies 
```sh
npm install
```

### Configure config.py
Edit the `config.py` file with your email credentials and MongoDB connection.

# config.py

MONGO_URI = `'mongodb://localhost:27017/mfa_project' ` # Local Mongo or Atlas URI
SECRET_KEY = 'your_secret_key_here'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'your_email@gmail.com'
MAIL_PASSWORD 'your_email_password_or_app_password'
MAIL_DEFAULT_SENDER = 'your_email@gmail.com' 

---

### Run MongoDB

If using MongoDB locally, make sure mongod is running.
If using MongoDB Atlas, replace MONGO_URI with your cloud connection string.

### Run the Application

```sh
export FLASK_APP=app.py
flask run
```

Open the app in your browser at:
https://humble-orbit-5gxrgrwpp5ggcv56r-5000.app.github.dev/login
 