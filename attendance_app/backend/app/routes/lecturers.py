# backend/app/routes/lecturers.py

"""
lecturers.py\n
Routes for lecturer dashboard, profile, and class attendance management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app import schemas, crud, models
from app.database import get_db
from app.utils import security
from fastapi import UploadFile, File
from app.utils.storage import upload_profile_image

router = APIRouter(
    prefix="/lecturers",
    tags=["Lecturers"]
)

# -------------------------
# Get logged-in lecturer profile
# -------------------------
@router.get("/me", response_model=schemas.LecturerOut)
def get_my_profile(current_lecturer=Depends(security.get_current_lecturer)):
    return current_lecturer

# -------------------------
# Update lecturer profile
# -------------------------
@router.put("/update", response_model=schemas.LecturerOut)
def update_lecturer_profile(
    updates: schemas.LecturerBase,
    db: Session = Depends(get_db),
    current_lecturer=Depends(security.get_current_lecturer)
):
    if updates.email:
        if crud.lecturer_email_exists(db, updates.email, exclude_id=current_lecturer.id):
            raise HTTPException(status_code=400, detail="Email already in use")

    updated = crud.update_lecturer(db, current_lecturer.id, current_lecturer.school_id, updates.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Lecturer not found")
    return updated

# change lecturer password
@router.put("/change-password")
def change_lecturer_password(
    payload: schemas.ChangePassword,
    db: Session = Depends(get_db),
    current_lecturer=Depends(security.get_current_lecturer)
):
    success = crud.change_lecturer_password(
        db,
        current_lecturer,
        payload.current_password,
        payload.new_password
    )

    if not success:
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    return {"message": "Password updated successfully"}


# upload profile image
@router.post("/profile/image")
def upload_profile_image_lecturer(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(security.get_current_lecturer)
):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid image type")

    image_url = upload_profile_image(file, current_user.id)

    current_user.profile_image = image_url
    db.commit()

    return {
        "profile_image": image_url
    }

# deactivate lecturer account
@router.delete("/deactivate")
def deactivate_lecturer(
    db: Session = Depends(get_db),
    current_lecturer=Depends(security.get_current_lecturer)
):
    current_lecturer.is_active = False
    db.commit()
    return {"detail": "Account deactivated successfully"}

# -------------------------
# View all students
# -------------------------
@router.get("/students", response_model=List[schemas.StudentOut])
def get_all_students(
    db: Session = Depends(get_db),
    current_lecturer: models.Lecturer = Depends(security.get_current_lecturer)
):
    students = crud.get_all_students(db, current_lecturer.school_id)
    return students


# -------------------------
# View all attendance records
# -------------------------
@router.get("/me/attendance", response_model=List[schemas.AttendanceOut])
def get_all_attendance_records(
    db: Session = Depends(get_db),
    current_user: models.Lecturer = Depends(security.get_current_lecturer)
):
    records = crud.get_attendance_for_lecturer(db, current_user.id, current_user.school_id)
    return records


# -------------------------------------------------------
# NEW (PHASE 2): Create class attendance session
# -------------------------------------------------------
@router.post("/create_session", response_model=schemas.AttendanceSessionOut)
def create_attendance_session(
    session_in: schemas.AttendanceSessionCreate,
    db: Session = Depends(get_db),
    current_lecturer=Depends(security.get_current_lecturer)
):
    """Lecturer creates a new attendance session with unique session code"""

    session = crud.create_attendance_session(db, session_in, lecturer_id=current_lecturer.id, lecturer_name=current_lecturer.full_name, school_id=current_lecturer.school_id)
    return session

@router.get("/me/sessions")
def get_my_sessions(
    db: Session = Depends(get_db),
    current_lecturer: models.Lecturer = Depends(security.get_current_lecturer),
):
    return (
        db.query(models.AttendanceSession)
        .filter(models.AttendanceSession.lecturer_id == current_lecturer.id)
        .order_by(models.AttendanceSession.created_at.desc())
        .all()
    )

# Close session
@router.post("/sessions/{session_id}/close")
def close_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_lecturer: models.Lecturer = Depends(security.get_current_lecturer),
):
    session = db.query(models.AttendanceSession).filter(
        models.AttendanceSession.id == session_id,
        models.AttendanceSession.lecturer_id == current_lecturer.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.is_active = False
    session.closed_at = datetime.utcnow()

    db.commit()
    return {"message": "Session closed successfully"}
