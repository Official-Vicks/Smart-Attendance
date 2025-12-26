"""
security.py
Handles:
- Token-based authentication (JWT creation & verification)
- Current user retrieval
- Role-based access control (student or lecturer)
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app import models, crud
from app.config import settings

bearer_scheme = HTTPBearer()

# ------------------------------------
# JWT: Create Access Token
# ------------------------------------
def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Generate a JWT access token.
    - data: dictionary containing user data (email, role, user_id)
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

# ------------------------------------
# Decode token and get payload
# ------------------------------------
def verify_token(token: str):
    """Decode JWT token and return payload if valid"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

# ------------------------------------
# Retrieve current logged-in user
# ------------------------------------
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials  # <-- RAW JWT
    payload = verify_token(token)

    email = payload.get("email")
    role = payload.get("role")

    if not email or not role:
        raise HTTPException(status_code=401, detail="Invalid authentication data")

    # Fetch user
    if role == "student":
        user = crud.get_student_by_email(db, email)
    else:
        user = crud.get_lecturer_by_email(db, email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"role": role, "user": user}

# ------------------------------------
# Restrict to students only
# ------------------------------------
def get_current_student(current=Depends(get_current_user)):
    if current["role"] != "student":
        raise HTTPException(
            status_code=403,
            detail="Access restricted to students only"
        )
    return current["user"]

# ------------------------------------
# Restrict to lecturers only
# ------------------------------------
def get_current_lecturer(current=Depends(get_current_user)):
    if current["role"] != "lecturer":
        raise HTTPException(
            status_code=403,
            detail="Access restricted to lecturers only"
        )
    return current["user"]
