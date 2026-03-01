from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app import crud
from app.schemas import LoginRequest
from app.config import settings
from app.utils.security import create_access_token

router = APIRouter(prefix="/admin", tags=["Admin Auth"])


@router.post("/login")
def admin_login(payload: LoginRequest, db: Session = Depends(get_db)):
    admin = crud.authenticate_admin(db, payload.email, payload.password)

    if admin is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if admin == "inactive":
        raise HTTPException(status_code=403, detail="Admin account deactivated")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"email": admin.email,"role": "admin"}, 
        expires_delta= access_token_expires)

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": "admin"
    }
