from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models, schemas
from app.utils import security
from typing import List


# -------------------------------------------------------------------
# Router configuration
# -------------------------------------------------------------------

router = APIRouter(
    prefix="/test-attendance",
    tags=["Attendance Tests"],
)


# -------------------------------------------------------------------
# 1️⃣ Basic health check + DB connectivity test
# -------------------------------------------------------------------
@router.get("/ping")
def attendance_ping(
    db: Session = Depends(get_db),
    current_lecturer: models.Lecturer = Depends(security.get_current_lecturer),
):
    """
    Confirms:
    - Database connection works
    - Attendance table exists
    - Alembic migrations are applied
    """
    count = db.query(models.Attendance).count()
    return {
        "status": "ok",
        "attendance_records": count,
    }


# -------------------------------------------------------------------
# 2️⃣ Get ALL attendance records (minimal fields)
# -------------------------------------------------------------------
@router.get("/all")
def get_all_attendance(
    db: Session = Depends(get_db),
    current_lecturer: models.Lecturer = Depends(security.get_current_lecturer),
):
    """
    Returns a list of attendance records.
    Useful for quick frontend or DB verification.
    """
    records = (
        db.query(models.Attendance)
        .order_by(models.Attendance.date.desc())
        .all()
    )
    return records


# -------------------------------------------------------------------
# 3️⃣ Validate student_name snapshot integrity
# -------------------------------------------------------------------
@router.get("/validate-student-names")
def validate_student_names(
    db: Session = Depends(get_db),
    current_lecturer: models.Lecturer = Depends(security.get_current_lecturer),
):
    """
    Ensures no attendance record has NULL or empty student_name.
    Confirms migration + create_attendance logic is correct.
    """
    invalid = (
        db.query(models.Attendance)
        .filter(
            (models.Attendance.student_name == None)
            | (models.Attendance.student_name == "")
        )
        .count()
    )

    return {
        "invalid_records": invalid,
        "status": "clean" if invalid == 0 else "needs_fix",
    }


# -------------------------------------------------------------------
# 4️⃣ Filter attendance by course
# -------------------------------------------------------------------
@router.get("/by-course/{course_code}")
def attendance_by_course(
    course_code: str,
    db: Session = Depends(get_db),
    current_lecturer: models.Lecturer = Depends(security.get_current_lecturer),
):
    """
    Simulates lecturer filtering attendance by course.
    """
    return (
        db.query(models.Attendance)
        .filter(models.Attendance.course_code == course_code)
        .all()
    )


# -------------------------------------------------------------------
# 5️⃣ Filter attendance by date
# -------------------------------------------------------------------
@router.get("/by-date/{day}")
def attendance_by_date(
    day: date,
    db: Session = Depends(get_db),
    current_lecturer: models.Lecturer = Depends(security.get_current_lecturer),
):
    """
    Simulates lecturer filtering attendance by a specific date.
    Format: YYYY-MM-DD
    """
    return (
        db.query(models.Attendance)
        .filter(models.Attendance.date == day)
        .all()
    )


# -------------------------------------------------------------------
# 6️⃣ Filter attendance by student (ID)
# -------------------------------------------------------------------
@router.get("/by-student-id/{student_id}")
def attendance_by_student_id(
    student_id: int,
    db: Session = Depends(get_db),
    current_lecturer: models.Lecturer = Depends(security.get_current_lecturer),
):
    """
    Fetches all attendance records for a specific student ID.
    """
    return (
        db.query(models.Attendance)
        .filter(models.Attendance.student_id == student_id)
        .all()
    )


# -------------------------------------------------------------------
# 7️⃣ Filter attendance by student name (real-world scenario)
# -------------------------------------------------------------------
@router.get("/by-student-name/{name}")
def attendance_by_student_name(
    name: str,
    db: Session = Depends(get_db),
    current_lecturer: models.Lecturer = Depends(security.get_current_lecturer),
):
    """
    Allows lecturers to search attendance by student name.
    Uses partial matching (case-insensitive).
    """
    return (
        db.query(models.Attendance)
        .filter(models.Attendance.student_name.ilike(f"%{name}%"))
        .all()
    )


# -------------------------------------------------------------------
# 8️⃣ Detect duplicate attendance (data integrity test)
# -------------------------------------------------------------------
@router.get("/detect-duplicates")
def detect_duplicate_attendance(
    db: Session = Depends(get_db),
    current_lecturer: models.Lecturer = Depends(security.get_current_lecturer),
):
    """
    Detects if any student marked attendance more than once
    for the same session (should NEVER happen).
    """
    duplicates = (
        db.query(
            models.Attendance.student_id,
            models.Attendance.session_id,
            func.count(models.Attendance.id).label("count"),
        )
        .group_by(
            models.Attendance.student_id,
            models.Attendance.session_id,
        )
        .having(func.count(models.Attendance.id) > 1)
        .all()
    )

    return duplicates


# -------------------------------------------------------------------
# 9️⃣ Serialization check (FastAPI response validation)
# -------------------------------------------------------------------
@router.get(
    "/serialization-check",
    response_model=List[schemas.AttendanceOut],
)
def serialization_check(
    db: Session = Depends(get_db),
    current_lecturer: models.Lecturer = Depends(security.get_current_lecturer),
):
    """
    Forces FastAPI to serialize Attendance using AttendanceOut.
    If this route fails, your response model is mismatched.
    """
    return db.query(models.Attendance).limit(5).all()
