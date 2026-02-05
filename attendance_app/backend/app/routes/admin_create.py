# app/routes/admin_bootstrap.py
import os
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Admin
from app.schemas import AdminCreate
from app.crud import get_password_hash

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/bootstrap")
def bootstrap_admin(
    admin: AdminCreate,
    db: Session = Depends(get_db),
    x_admin_key: str = Header(...)
):
    if x_admin_key != os.getenv("ADMIN_BOOTSTRAP_KEY"):
        raise HTTPException(status_code=403, detail="Forbidden")

    if db.query(Admin).filter(Admin.email == admin.email).first():
        raise HTTPException(status_code=400, detail="Admin already exists")

    new_admin = Admin(
        email=admin.email,
        hashed_password=get_password_hash(admin.password),
        is_active=True
    )
    db.add(new_admin)
    db.commit()

    return {"message": "Admin created successfully"}
