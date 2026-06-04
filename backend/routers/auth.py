from fastapi import APIRouter, Depends, HTTPException, status
from json_db import JSONDatabase
from datetime import datetime, timedelta
import models
import schemas
from database import get_db
from auth import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    send_otp,
    get_otp,
    delete_otp,
    send_faculty_welcome_email,
    send_password_reset_email,
    ALGORITHM,
    SECRET_KEY
)
import jose.jwt as jwt

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/signup")
def signup(user: schemas.SignupRequest, db: JSONDatabase = Depends(get_db)):
    """Register a new user directly (no OTP verification)"""
    # Restrict roles
    if user.role not in ["student", "author"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Public registration is only available for Student and Faculty roles."
        )

    # Check if email already exists
    users = db.read("users")
    existing_user = next((u for u in users if u.get("email", "").lower() == user.email.lower()), None)
    
    if existing_user:
        # If it's an author re-addition, just update and re-send welcome email
        if user.role == "author" and existing_user.get("role") == "author":
            hashed_password = get_password_hash(user.password)
            db.update("users", existing_user["id"], {
                "name": user.name,
                "password_hash": hashed_password
            })
            email_sent = send_faculty_welcome_email(user.email, user.password, user.name)
            return {
                "access_token": "re-added", 
                "token_type": "bearer",
                "role": "author",
                "otp_required": False,
                "email_sent": email_sent
            }
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Please login or use a different email."
        )
    
    # Create user directly without OTP
    hashed_password = get_password_hash(user.password)
    new_user = {
        "username": user.username or user.email,
        "email": user.email.lower(),
        "name": user.name,
        "role": user.role,
        "branch": user.branch,
        "year": user.year,
        "semester": user.semester,
        "password_hash": hashed_password,
        "created_at": datetime.utcnow().isoformat()
    }
    saved_user = db.add("users", new_user)
    
    # Send welcome email if it's an author
    email_sent = False
    if user.role == "author":
        email_sent = send_faculty_welcome_email(user.email, user.password, user.name)
    
    # Issue token immediately
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": saved_user["email"], "role": saved_user["role"]},
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": saved_user["role"],
        "otp_required": False,
        "email_sent": email_sent
    }

@router.post("/login")
def login(login_data: schemas.LoginRequest, db: JSONDatabase = Depends(get_db)):
    """Initial login: verify credentials and trigger OTP"""
    # Find user by email
    users = db.read("users")
    email_key = login_data.email.lower()
    user = next((u for u in users if u.get("email", "").lower() == email_key), None)
    
    # Specific error if not registered
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email is not registered yet. Please create an account first."
        )
    
    # Verify password
    if not verify_password(login_data.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )
    
    # Verify name if provided (for dedicated faculty login)
    if login_data.name and user.get("name", "").lower() != login_data.name.lower():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Provided name does not match our records for this email.",
        )
    
    # Credentials verified, bypass OTP and login directly for all roles
    from .auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": user["role"],
        "otp_required": False
    }

@router.post("/verify-otp")
def verify_otp(data: schemas.VerifyOTPRequest, db: JSONDatabase = Depends(get_db)):
    """Verify OTP and either create account (signup) or issue token (login)"""
    email_key = data.email.lower()
    stored = get_otp(email_key)
    
    if not stored:
        raise HTTPException(status_code=400, detail="Verification code not requested or expired")
    
    if stored["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    # Check expiry (stored as ISO string if loaded from JSON)
    expires = stored["expires"]
    if isinstance(expires, str):
        expires = datetime.fromisoformat(expires)
        
    if datetime.utcnow() > expires:
        delete_otp(email_key)
        raise HTTPException(status_code=400, detail="Verification code expired")
    
    signup_data = stored.get("signup_data")
    
    # Clear OTP
    delete_otp(email_key)
    
    if signup_data:
        # Complete signup: save to DB
        hashed_password = get_password_hash(signup_data["password"])
        new_user = {
            "username": signup_data.get("username") or signup_data["email"],
            "email": signup_data["email"].lower(),
            "name": signup_data["name"],
            "role": signup_data["role"],
            "branch": signup_data.get("branch"),
            "year": signup_data.get("year"),
            "semester": signup_data.get("semester"),
            "password_hash": hashed_password,
            "created_at": datetime.utcnow().isoformat()
        }
        user = db.add("users", new_user)
        role = user["role"]
        email = user["email"]
    else:
        # Complete login: find existing user
        users = db.read("users")
        user = next((u for u in users if u.get("email", "").lower() == email_key), None)
        if not user:
            raise HTTPException(status_code=404, detail="User lost during verification")
        role = user["role"]
        email = user["email"]

    # Issue token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": email, "role": role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": role}

@router.get("/me", response_model=schemas.User)
def get_current_user_info(current_user: models.User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.post("/forgot-password")
def forgot_password(data: schemas.ForgotPasswordRequest, db: JSONDatabase = Depends(get_db)):
    """Generate and send password reset link"""
    users = db.read("users")
    user = next((u for u in users if u.get("email", "").lower() == data.email.lower()), None)
    
    if not user:
        # Don't reveal if user exists for security, just return success
        return {"message": "If this email is registered, a reset link will be sent."}
    
    # Verify name for authors (condition from author login)
    if user.get("role") == "author" and data.name:
        if user.get("name", "").lower() != data.name.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Provided name does not match our records for this email.",
            )
    elif user.get("role") == "author" and not data.name:
        # If accessing from author login but no name provided in request
        # This might happen if the frontend doesn't send it, but we should handle it
        pass

    # Create reset token with short expiry
    reset_token = create_access_token(
        data={"sub": user["email"], "type": "reset_password", "role": user["role"]},
        expires_delta=timedelta(minutes=15)
    )
    
    send_password_reset_email(user["email"], reset_token, user["role"])
    return {"message": "Success! Check your email for the reset link."}

@router.post("/reset-password")
def reset_password(data: schemas.ResetPasswordRequest, db: JSONDatabase = Depends(get_db)):
    """Reset password using token"""
    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        token_type = payload.get("type")
        
        if email is None or token_type != "reset_password":
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
            
        users = db.read("users")
        user = next((u for u in users if u.get("email", "").lower() == email.lower()), None)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Update password
        new_password_hash = get_password_hash(data.new_password)
        db.update("users", user["id"], {"password_hash": new_password_hash})
        
        return {"message": "Password updated successfully! You can now login."}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
