from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from app.utils.security import get_current_admin

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.get("/me")
def get_admin_profile(current_admin=Depends(get_current_admin)):
    return {
        "id": current_admin.id,
        "full_name": current_admin.full_name,
        "email": current_admin.email
    }

@router.get("/students")
def admin_list_students(
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    students = db.query(models.Student).all()

    return [
        {
            "id": s.id,
            "full_name": s.full_name,
            "email": s.email,
            "registration_number": s.registration_number,
            "department": s.department,
            "is_active": s.is_active
        }
        for s in students
    ]

@router.get("/lecturers")
def admin_list_lecturers(
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    lecturers = db.query(models.Lecturer).all()

    return [
        {
            "id": l.id,
            "full_name": l.full_name,
            "email": l.email,
            "course": l.course,
            "is_active": l.is_active
        }
        for l in lecturers
    ]

from fastapi import HTTPException

@router.patch("/deactivate/{role}/{user_id}")
def admin_deactivate_account(
    role: str,
    user_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    if role == "student":
        user = db.query(models.Student).filter(models.Student.id == user_id).first()
    elif role == "lecturer":
        user = db.query(models.Lecturer).filter(models.Lecturer.id == user_id).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid role")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()

    return {"message": f"{role.capitalize()} account deactivated"}

@router.patch("/reactivate/{role}/{user_id}")
def admin_reactivate_account(
    role: str,
    user_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    if role == "student":
        user = db.query(models.Student).filter(models.Student.id == user_id).first()
    elif role == "lecturer":
        user = db.query(models.Lecturer).filter(models.Lecturer.id == user_id).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid role")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    db.commit()

    return {"message": f"{role.capitalize()} account reactivated"}
