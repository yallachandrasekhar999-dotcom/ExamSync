from datetime import datetime, timedelta
from typing import Optional
import os
import json
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import bcrypt
from database import get_db
from json_db import JSONDatabase
import models
from dotenv import load_dotenv

load_dotenv()

# SMTP configuration from .env
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 43200 # 30 days

# Persistent OTP storage for development reloads
OTP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "otp_storage.json")

def load_otp_storage():
    if not os.path.exists(OTP_FILE):
        return {}
    try:
        with open(OTP_FILE, 'r') as f:
            data = json.load(f)
            # Convert expiry strings back to datetime
            for email in data:
                data[email]["expires"] = datetime.fromisoformat(data[email]["expires"])
            return data
    except:
        return {}

def save_otp_storage(storage):
    os.makedirs(os.path.dirname(OTP_FILE), exist_ok=True)
    serializable = {}
    for email in storage:
        item = storage[email].copy()
        item["expires"] = item["expires"].isoformat()
        serializable[email] = item
    with open(OTP_FILE, 'w') as f:
        json.dump(serializable, f)

def send_otp(email: str, signup_data: Optional[dict] = None):
    """Generate and send OTP via email"""
    otp = str(random.randint(100000, 999999))
    storage = load_otp_storage()
    storage[email.lower()] = {
        "otp": otp,
        "expires": datetime.utcnow() + timedelta(minutes=5),
        "signup_data": signup_data
    }
    save_otp_storage(storage)
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = email
        msg['Subject'] = "Exam Sync - Your Verification Code"
        
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #6c63ff; text-align: center;">Verification Code</h2>
                    <p>Hello,</p>
                    <p>Your verification code for Exam Sync is:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <span style="font-size: 32px; font-weight: bold; color: #1a1a2e; letter-spacing: 5px; background: #f0f0f0; padding: 10px 20px; border-radius: 5px;">{otp}</span>
                    </div>
                    <p>This code will expire in 5 minutes. If you did not request this, please ignore this email.</p>
                    <hr style="border: 0; border-top: 1px solid #eee;">
                    <p style="font-size: 12px; color: #888; text-align: center;">Exam Sync Platform &copy; 2026</p>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

def send_faculty_welcome_email(email: str, password: str, name: str):
    """Send welcome email to newly created faculty with their credentials"""
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Exam Sync <{EMAIL_USER}>"
        msg['To'] = email
        msg['Subject'] = "Exam Sync - Your Faculty Account Credentials"
        
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #6c63ff; text-align: center;">Welcome to Exam Sync</h2>
                    <p>Hello <strong>{name}</strong>,</p>
                    <p>An administrator has created a faculty account for you on the Exam Sync platform.</p>
                    <p>You can now log in using the following credentials:</p>
                    <div style="background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0; border: 1px solid #eee;">
                        <p style="margin: 5px 0;"><strong>Username / Email:</strong> {email}</p>
                        <p style="margin: 5px 0;"><strong>Password:</strong> {password}</p>
                    </div>
                    <p>You can log in at: <a href="http://localhost:8000/faculty_login.html" style="color: #6c63ff; font-weight: bold;">Login to Exam Sync</a></p>
                    <p>Once logged in, you can manage the curriculum and content for your assigned subjects.</p>
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;">
                    <p style="font-size: 12px; color: #888; text-align: center;">Exam Sync Platform &copy; 2026</p>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        error_msg = f"SMTP Error: {str(e)}"
        print(error_msg)
        try:
            with open("smtp_error.log", "a") as f:
                f.write(f"[{datetime.utcnow().isoformat()}] {error_msg}\n")
        except:
            pass
        return False

def send_password_reset_email(email: str, token: str, role: Optional[str] = None):
    """Send password reset link to user"""
    try:
        reset_link = f"http://localhost:8000/reset_password.html?token={token}"
        if role:
            reset_link += f"&role={role}"
        msg = MIMEMultipart()
        msg['From'] = f"Exam Sync <{EMAIL_USER}>"
        msg['To'] = email
        msg['Subject'] = "Exam Sync - Reset Your Password"
        
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #00c9a7; text-align: center;">Reset Your Password</h2>
                    <p>Hello,</p>
                    <p>We received a request to reset your password for your Exam Sync account.</p>
                    <p>Click the button below to set a new password:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" style="background: linear-gradient(90deg, #00c9a7, #00897b); color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Reset Password</a>
                    </div>
                    <p>If you did not request this, please ignore this email. This link will expire in 15 minutes.</p>
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;">
                    <p style="font-size: 12px; color: #888; text-align: center;">Exam Sync Platform &copy; 2026</p>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

def get_otp(email: str):
    """Retrieve OTP data from persistent storage"""
    storage = load_otp_storage()
    return storage.get(email.lower())

def delete_otp(email: str):
    """Delete OTP data from persistent storage"""
    storage = load_otp_storage()
    if email.lower() in storage:
        del storage[email.lower()]
        save_otp_storage(storage)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Hash a password"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password[:72].encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: JSONDatabase = Depends(get_db)):
    """Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # JSON retrieval
    users = db.read("users")
    user_data = next((u for u in users if u.get("email", "").lower() == email.lower()), None)
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User not found for token sub: {email}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return models.User(**user_data)

def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    """Ensure the user is active (can add more checks here)"""
    return current_user

def require_role(allowed_roles: list):
    """Dependency to check if user has required role"""
    def role_checker(current_user: models.User = Depends(get_current_active_user)):
        # Most robust way to get the string value of a role (Enum-safe)
        user_role = str(current_user.role.value if hasattr(current_user.role, 'value') else current_user.role).lower()
        allowed_list = [str(r).lower() for r in allowed_roles]
        
        if user_role not in allowed_list:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions for role: {user_role}"
            )
        return current_user
    return role_checker
