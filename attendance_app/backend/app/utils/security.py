"""
security.py
Handles:
- Token-based authentication (JWT creation & verification)
- Current user retrieval
- Role-based access control (student, lecturer, admin)
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app import models, crud
from app.config import settings
from app.core.request_context import user_id_ctx, school_id_ctx, role_ctx

bearer_scheme = HTTPBearer()

# ------------------------------------
# JWT: Create Access Token
# ------------------------------------
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()

    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))

    to_encode.update({
        "exp": expire,
        "sub": str(data.get("user_id"))  # standard JWT subject
    })

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
async def get_current_user(   # ✅ CHANGED TO ASYNC
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = verify_token(token)

    request.state.user = payload  # optional (still useful)

    email = payload.get("email")
    role = payload.get("role")
    school_id = payload.get("school_id")

    if not email or not role:
        raise HTTPException(status_code=401, detail="Invalid authentication data")

    # Fetch user from DB
    if role == "student":
        user = crud.get_student_by_email(db, email, school_id)
    elif role == "lecturer":
        user = crud.get_lecturer_by_email(db, email, school_id)
    elif role == "admin":
        user = crud.get_admin_by_email(db, email)
    else:
        raise HTTPException(status_code=401, detail="Invalid role")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Account is deactivated"
        )

    # 🔥 SET LOGGING CONTEXT (trusted DB data)
    user_id_ctx.set(str(user.id))
    school_id_ctx.set(str(user.school_id) if hasattr(user, "school_id") else None)
    role_ctx.set(role)

    return {"role": role, "user": user}


# ------------------------------------
# Restrict to students only
# ------------------------------------
async def get_current_student(   # ✅ ASYNC
    current=Depends(get_current_user)
):
    if current["role"] != "student":
        raise HTTPException(
            status_code=403,
            detail="Access restricted to students only"
        )
    return current["user"]


# ------------------------------------
# Restrict to lecturers only
# ------------------------------------
async def get_current_lecturer(   # ✅ ASYNC
    current=Depends(get_current_user)
):
    if current["role"] != "lecturer":
        raise HTTPException(
            status_code=403,
            detail="Access restricted to lecturers only"
        )
    return current["user"]


# ------------------------------------
# Restrict to admins only
# ------------------------------------
async def get_current_admin(   # ✅ ASYNC
    current=Depends(get_current_user)
):
    if current["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access only"
        )

    admin = current["user"]

    if not admin.is_active:
        raise HTTPException(
            status_code=403,
            detail="Admin account deactivated"
        )

    return admin