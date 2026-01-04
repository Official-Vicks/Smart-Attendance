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

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)

# -------------------------
# Get logged-in student profile
# -------------------------
@router.get("/me", response_model=schemas.StudentOut)
def get_my_profile(current_student=Depends(security.get_current_student)):
    return current_student


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

    updated = crud.update_student(db, current_student.id, updates.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Student not found")
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

    return {"message": "Password updated successfully"}


# -------------------------
# Get my attendance records
# -------------------------
@router.get("/me/attendance", response_model=List[schemas.MyAttendanceOut])
def get_my_attendance_records(
    db: Session = Depends(get_db),
    current_user: models.Student = Depends(security.get_current_student)
):
    records = crud.get_attendance_by_student(db, current_user.id)
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
# NEW (PHASE 2): Verify attendance session code
# -------------------------------------------------------
@router.post("/verify_session_code", response_model=schemas.AttendanceSessionOut)
def verify_session_code(
    session_code: str,
    db: Session = Depends(get_db),
    current_student=Depends(security.get_current_student)
):
    """Student enters the generated attendance code to access session"""

    session = crud.get_session_by_code(db, session_code)

    if not session.is_active or session.date < date.today():
        raise HTTPException(status_code=400, detail="Session is expired")

    if not session:
        raise HTTPException(status_code=404, detail="Invalid or expired session code")

    return session
