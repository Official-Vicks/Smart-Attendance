# backend/app/routes/lecturers.py

"""
lecturers.py
Routes for lecturer dashboard, profile, and class attendance management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud, models
from app.database import get_db
from app.utils.security import get_current_lecturer

router = APIRouter(
    prefix="/lecturers",
    tags=["Lecturers"]
)

# -------------------------
# Get logged-in lecturer profile
# -------------------------
@router.get("/me", response_model=schemas.LecturerOut)
def get_my_profile(current_lecturer=Depends(get_current_lecturer)):
    return current_lecturer


# -------------------------
# Update lecturer profile
# -------------------------
@router.put("/update", response_model=schemas.LecturerOut)
def update_lecturer_profile(
    updates: schemas.LecturerBase,
    db: Session = Depends(get_db),
    current_lecturer=Depends(get_current_lecturer)
):
    updated = crud.update_lecturer(db, current_lecturer.id, updates.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Lecturer not found")
    return updated


# -------------------------
# View all students
# -------------------------
@router.get("/students", response_model=List[schemas.StudentOut])
def get_all_students(
    db: Session = Depends(get_db),
    current_lecturer=Depends(get_current_lecturer)
):
    students = crud.get_student(db)
    return students


# -------------------------
# View all attendance records
# -------------------------
@router.get("/me/attendance", response_model=List[schemas.AttendanceOut])
def get_all_attendance_records(
    db: Session = Depends(get_db),
    current_user: models.Lecturer = Depends(get_current_lecturer)
):
    records = crud.get_attendance_for_lecturer(db, current_user.id)
    return records


# -------------------------------------------------------
# NEW (PHASE 2): Create class attendance session
# -------------------------------------------------------
@router.post("/create_session", response_model=schemas.AttendanceSessionOut)
def create_attendance_session(
    session_in: schemas.AttendanceSessionCreate,
    db: Session = Depends(get_db),
    current_lecturer=Depends(get_current_lecturer)
):
    """Lecturer creates a new attendance session with unique session code"""

    session = crud.create_attendance_session(db, session_in, lecturer_id=current_lecturer.id)
    return session