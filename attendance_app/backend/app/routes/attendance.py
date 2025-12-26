# ======================================================
# Attendance Routes
# Handles marking and viewing of attendance records.
# ======================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from typing import List
from app.database import get_db
from app import crud, schemas, models
from app.utils import security

router = APIRouter(prefix="/attendance", tags=["Attendance"])


# ======================================================
# Mark Attendance (Student)
# ======================================================
@router.post("/mark", response_model=schemas.AttendanceSessionOut)
def mark_attendance(
    attendance_data: schemas.AttendanceSessionCreate,
    db: Session = Depends(get_db),
    current_user: models.Student = Depends(security.get_current_student)
):
    """
    Allows a student to mark attendance for a specific session.
    Prevents duplicate attendance per session.
    """

    # Get the session
    session = crud.get_attendance_session_by_id(
        db=db,
        session_id=attendance_data.session_id
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance session not found"
        )

    #Prevent duplicate attendance for this session
    existing = crud.get_attendance_by_student_and_session(
        db=db,
        student_id=current_user.id,
        session_id=session.id
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attendance already marked for this session"
        )

    # Create attendance with course snapshot
    new_attendance = crud.create_attendance(
        db=db,
        student_id=current_user.id,
        lecturer_id=session.lecturer_id,
        session_id=session.id,
        course_code=session.course_code,
        course_title=session.course_title,
        date=session.date,
        status="present"
    )

    return new_attendance


# ======================================================
# View Attendance (Lecturer)
# ======================================================
@router.get("/records", response_model=List[schemas.AttendanceOut])
def view_attendance_records(
    date_filter: date = None,
    db: Session = Depends(get_db),
    current_user: models.Lecturer = Depends(security.get_current_lecturer)
):
    """
    Allows a lecturer to view attendance records.
    Automatically filters by lecturer_id.
    """

    # Get all attendance for this lecturer
    records = crud.get_attendance_for_lecturer(db, lecturer_id=current_user.id)

    # Optional filter
    if date_filter:
        records = [record for record in records if record.date == date_filter]

    return records


# ======================================================
# Delete Attendance (Lecturer)
# ======================================================
@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendance_record(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: models.Lecturer = Depends(security.get_current_lecturer)
):
    """
    Allows a lecturer to delete a student's attendance record.
    Only deletes if the record belongs to the logged-in lecturer.
    """

    attendance = crud.get_attendance_by_id(db, attendance_id)

    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")

    if attendance.lecturer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    crud.delete_attendance(db, attendance_id)

    # FIX: indentation — MUST align with function body, not outside it
    return {"message": "Deleted successfully"}

@router.get("/session/{session_id}/status")
def check_attendance_status(
    session_id: int,
    db: Session = Depends(get_db),
    current_student: models.Student = Depends(security.get_current_student)
):
    attendance = crud.get_attendance_by_student_and_session(
        db=db,
        student_id=current_student.id,
        session_id=session_id
    )

    return {
        "marked": attendance is not None
    }