# backend/app/routes/students.py

"""
students.py
Routes for student dashboard, profile, and attendance records.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List
from app import schemas, crud, models
from app.database import get_db
from app.utils import security
from fastapi import UploadFile, File
from app.utils.storage import upload_profile_image
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)

# -------------------------
# Get logged-in student profile
# -------------------------
@router.get("/me", response_model=schemas.StudentOut)
def get_my_profile(db: Session = Depends(get_db), current_student: models.Student = Depends(security.get_current_student)):
    school = crud.get_school_by_id(db, current_student.school_id)
    
    return {
        "id": current_student.id,
        "full_name": current_student.full_name,
        "email": current_student.email,
        "registration_number": current_student.registration_number,
        "department": current_student.department,
        "profile_image": current_student.profile_image,
        "school_name": school.name,
        "school_id": current_student.school_id
    }

# -------------------------
# Update profile
# -------------------------
@router.put("/update", response_model=schemas.StudentOut)
def update_student_profile(
    updates: schemas.StudentBase,
    db: Session = Depends(get_db),
    current_student=Depends(security.get_current_student)
):
    if updates.email:
        if crud.student_email_exists(db, updates.email, exclude_id=current_student.id):
            raise HTTPException(status_code=400, detail="Email already in use")

    updated = crud.update_student(db, current_student.id, current_student.school_id, updates.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Student not found")
    
    logger.info(f"Student: {current_student.full_name} updated profile")
    return updated

# change password
@router.put("/change-password")
def change_student_password(
    payload: schemas.ChangePassword,
    db: Session = Depends(get_db),
    current_student=Depends(security.get_current_student)
):
    success = crud.change_student_password(
        db,
        current_student,
        payload.current_password,
        payload.new_password
    )

    if not success:
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    logger.info(f"Student: {current_student.full_name} changed password")

    return {"message": "Password updated successfully"}

# update profile image
@router.post("/profile/image")
def upload_profile_image_student(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_student=Depends(security.get_current_student)
):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid image type")

    image_url = upload_profile_image(file, current_student.id)

    current_student.profile_image = image_url

    logger.info(f"Student: {current_student.full_name} uploaded profile image {image_url}")
    db.commit()

    return {
        "profile_image": image_url
    }

# deactivate student account
@router.delete("/deactivate")
def deactivate_student(
    db: Session = Depends(get_db),
    current_student=Depends(security.get_current_student)
):
    current_student.is_active = False
    logger.info(f"Student: {current_student.full_name} account deactivated")
    db.commit()
    return {"detail": "Account deactivated successfully"}

# -------------------------
# Get my attendance records
# -------------------------
@router.get("/me/attendance", response_model=List[schemas.MyAttendanceOut])
def get_my_attendance_records(
    db: Session = Depends(get_db),
    current_user: models.Student = Depends(security.get_current_student)
):
    records = crud.get_attendance_by_student(db, current_user.id, current_user.school_id)
    output = []
    for rec in records:
        output.append({
            "id": rec.id,
            "date": rec.date,
            "status": rec.status,
            "course_title": rec.course_title,
            "course_code": rec.course_code,
            "lecturer_name": rec.lecturer_name
        })
    return output


# -------------------------------------------------------
# Verify attendance session code
# -------------------------------------------------------
@router.post("/verify_session_code", response_model=schemas.AttendanceSessionOut)
def verify_session_code(
    session_code: str,
    db: Session = Depends(get_db),
    current_student=Depends(security.get_current_student)
):
    """Student enters the generated attendance code to access session"""

    session = crud.get_session_by_code(db, session_code, current_student.school_id)

    if not session:
        raise HTTPException(status_code=404, detail="Invalid or expired session code")

    if not session.is_active or session.date < date.today():
        raise HTTPException(status_code=400, detail="Session is expired")

    return session