"""
crud.py
CRUD operations for Smart Attendance System.
"""

from sqlalchemy.orm import Session
from app import models, schemas
from passlib.context import CryptContext
from datetime import datetime, timedelta, date
from jose import jwt, JWTError
from app.config import settings
from typing import Optional, Dict
import uuid


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ----------------------------
# Password helpers
# ----------------------------
def get_password_hash(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password too long (max 72 characters).")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ----------------------------
# JWT helpers
# ----------------------------
def decode_access_token(token: str) -> Optional[Dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


# ----------------------------
# Lecturer CRUD
# ----------------------------

def change_lecturer_password(db: Session, lecturer, current_password: str, new_password: str):
    if not verify_password(current_password, lecturer.hashed_password):
        return False

    lecturer.hashed_password = get_password_hash(new_password)
    db.commit()
    return True
    

def update_lecturer(db: Session, lecturer_id: int, updates: dict):
    lecturer = (
        db.query(models.Lecturer)
        .filter(models.Lecturer.id == lecturer_id)
        .first()
    )

    if not lecturer:
        return None

    ALLOWED_FIELDS = {"full_name", "email", "course"}

    for field, value in updates.items():
        if field in ALLOWED_FIELDS and value is not None:
            setattr(lecturer, field, value)


    db.commit()
    db.refresh(lecturer)

    return lecturer

def get_lecturer_by_email(db: Session, email: str):
    return (
        db.query(models.Lecturer)
        .filter(models.Lecturer.email == email)
        .first()
    )


def lecturer_email_exists(db: Session, email: str, exclude_id: Optional[int] = None) -> bool:
    query = db.query(models.Lecturer).filter(models.Lecturer.email == email)

    if exclude_id:
        query = query.filter(models.Lecturer.id != exclude_id)

    return db.query(query.exists()).scalar()

def get_lecturer(db: Session, lecturer_id: int):
    return db.query(models.Lecturer).filter(models.Lecturer.id == lecturer_id).first()

def create_lecturer(db: Session, lecturer_in: schemas.LecturerCreate):
    if get_lecturer_by_email(db, lecturer_in.email):
        raise ValueError("Lecturer with this email already exists")

    lecturer = models.Lecturer(
        full_name=lecturer_in.full_name,
        email=lecturer_in.email,
        hashed_password=get_password_hash(lecturer_in.password),
        course=lecturer_in.course
    )
    db.add(lecturer)
    db.commit()
    db.refresh(lecturer)
    return lecturer


def authenticate_lecturer(db: Session, email: str, password: str):
    lecturer = get_lecturer_by_email(db, email)
    if not lecturer or not verify_password(password, lecturer.hashed_password):
        return False
    if not lecturer or not lecturer.is_active:
        return False
    return lecturer


# ----------------------------
# Student CRUD
# ----------------------------
def change_student_password(db: Session, student, current_password: str, new_password: str):
    if not verify_password(current_password, student.hashed_password):
        return False

    student.hashed_password = get_password_hash(new_password)
    db.commit()
    return True


def update_student(db: Session, student_id: int, updates: dict):
    student = (
        db.query(models.Student)
        .filter(models.Student.id == student_id)
        .first()
    )

    if not student:
        return None

    ALLOWED_FIELDS = {"full_name", "email", "department", "reg_no"}

    for field, value in updates.items():
        if field in ALLOWED_FIELDS and value is not None:
            setattr(student, field, value)


    db.commit()
    db.refresh(student)

    return student

def get_student_by_email(db: Session, email: str):
    return (
        db.query(models.Student)
        .filter(models.Student.email == email)
        .first()
    )


def student_email_exists(db: Session, email: str, exclude_id: Optional[int] = None) -> bool:
    query = db.query(models.Student).filter(models.Student.email == email)

    if exclude_id:
        query = query.filter(models.Student.id != exclude_id)

    return db.query(query.exists()).scalar()

def get_student_by_registration(db: Session, reg_no: str):
    return db.query(models.Student).filter(models.Student.registration_number == reg_no).first()

def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def get_all_students(db: Session):
    return db.query(models.Student).all()

def create_student(db: Session, student_in: schemas.StudentCreate):
    if (get_student_by_email(db, student_in.email)
        or get_student_by_registration(db, student_in.registration_number)):
        raise ValueError("Student with this email or registration number already exists")

    student = models.Student(
        full_name=student_in.full_name,
        email=student_in.email,
        registration_number=student_in.registration_number,
        department=student_in.department,
        hashed_password=get_password_hash(student_in.password)
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def authenticate_student(db: Session, email: str, password: str):
    student = get_student_by_email(db, email)
    if not student or not verify_password(password, student.hashed_password):
        return False
    if not student or not student.is_active:
        return False
    return student


# ----------------------------
# Attendance CRUD
# ----------------------------
def get_attendance_by_student_and_date(db: Session, student_id: int, date_value: date):
    return (
        db.query(models.Attendance)
        .filter(models.Attendance.student_id == student_id)
        .filter(models.Attendance.date == date_value)
        .first()
    )

def get_attendance_by_course_and_date(db: Session, course_code: str, date_value: date):
    return (
        db.query(models.Attendance)
        .filter(models.Attendance.course_code == course_code)
        .filter(models.Attendance.date == date_value)
        .first()
    )
def get_attendance_by_student(db: Session, student_id: int):
    return (
        db.query(models.Attendance)
        .filter(models.Attendance.student_id == student_id)
        .order_by(models.Attendance.created_at.desc())
        .all()
    )

def create_attendance(
    db: Session,
    student_id: int,
    student_name: str,
    lecturer_id: int,
    lecturer_name: str,
    session_id: int,
    course_code: str,
    course_title: str,
    date:date,
    status: str = "present"
):
    attendance = models.Attendance(
        student_id=student_id,
        student_name=student_name,
        lecturer_id=lecturer_id,
        lecturer_name=lecturer_name,
        session_id=session_id,
        course_code=course_code,
        course_title=course_title,
        date=date,
        status=status
    )

    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance



# ----------------------------
# NEW: Attendance Session CRUD
# ----------------------------
def create_attendance_session(db: Session, session_in: schemas.AttendanceSessionCreate, lecturer_id:int, lecturer_name: str):
    """Create a new class attendance session with a unique session code."""

    unique_code = f"S-{uuid.uuid4().hex[:6].upper()}"

    session = models.AttendanceSession(
        lecturer_id=lecturer_id,
        lecturer_name= lecturer_name,
        course_code=session_in.course_code,
        course_title=session_in.course_title,
        date=session_in.date,
        session_code=unique_code,
        is_active= True
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session_by_code(db: Session, session_code: str):
    """Retrieve attendance session by unique code."""
    return (
        db.query(models.AttendanceSession)
        .filter(models.AttendanceSession.session_code == session_code)
        .first()
    )

def get_attendance_by_student_and_session(db, student_id: int, session_id: int):
    return (
        db.query(models.Attendance)
        .filter(
            models.Attendance.student_id == student_id,
            models.Attendance.session_id == session_id
        )
        .first()
    )

def get_attendance_for_lecturer(
    db: Session,
    lecturer_id: int,
    date: Optional[date] = None,
    course_code: Optional[str] = None
):
    query = db.query(models.Attendance).filter(
        models.Attendance.lecturer_id == lecturer_id
    )

    if date:
        query = query.filter(models.Attendance.date == date)

    if course_code:
        query = query.filter(models.Attendance.course_code == course_code)

    return query.all()

def get_attendance_by_id(db: Session, attendance_id: int):
    """Get a specific attendance record by ID"""
    return db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()

def delete_attendance(db: Session, attendance_id: int):
    """Delete a specific attendance record"""
    attendance = get_attendance_by_id(db, attendance_id)
    if attendance:
        db.delete(attendance)
        db.commit()

def get_attendance_session_by_id(db, session_id: int):
    return db.query(models.AttendanceSession).filter(
        models.AttendanceSession.id == session_id
    ).first()

def is_session_expired(session):
    return session.date < date.today()

# ======================
# ADMIN CRUD
# ======================

def get_admin_by_email(db: Session, email: str):
    return db.query(models.Admin).filter(models.Admin.email == email).first()


def authenticate_admin(db: Session, email: str, password: str):
    admin = get_admin_by_email(db, email)
    if not admin:
        return None
    if not verify_password(password, admin.hashed_password):
        return None
    if not admin.is_active:
        return "inactive"
    return admin
