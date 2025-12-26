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
def hash_password(password: str) -> str:
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
def get_lecturer_by_email(db: Session, email: str):
    return db.query(models.Lecturer).filter(models.Lecturer.email == email).first()

def get_lecturer(db: Session, lecturer_id: int):
    return db.query(models.Lecturer).filter(models.Lecturer.id == lecturer_id).first()

def create_lecturer(db: Session, lecturer_in: schemas.LecturerCreate):
    if get_lecturer_by_email(db, lecturer_in.email):
        raise ValueError("Lecturer with this email already exists")

    lecturer = models.Lecturer(
        full_name=lecturer_in.full_name,
        email=lecturer_in.email,
        hashed_password=hash_password(lecturer_in.password),
        course=lecturer_in.course
    )
    db.add(lecturer)
    db.commit()
    db.refresh(lecturer)
    return lecturer


def authenticate_lecturer(db: Session, email: str, password: str):
    lecturer = get_lecturer_by_email(db, email)
    if not lecturer or not verify_password(password, lecturer.hashed_password):
        return None
    return lecturer


# ----------------------------
# Student CRUD
# ----------------------------
def get_student_by_email(db: Session, email: str):
    return db.query(models.Student).filter(models.Student.email == email).first()

def get_student_by_registration(db: Session, reg_no: str):
    return db.query(models.Student).filter(models.Student.registration_number == reg_no).first()

def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def create_student(db: Session, student_in: schemas.StudentCreate):
    if (get_student_by_email(db, student_in.email)
        or get_student_by_registration(db, student_in.registration_number)):
        raise ValueError("Student with this email or registration number already exists")

    student = models.Student(
        full_name=student_in.full_name,
        email=student_in.email,
        registration_number=student_in.registration_number,
        department=student_in.department,
        hashed_password=hash_password(student_in.password)
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def authenticate_student(db: Session, email: str, password: str):
    student = get_student_by_email(db, email)
    if not student or not verify_password(password, student.hashed_password):
        return None
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

def get_attendance_by_student(db: Session, student_id: int):
    return (
        db.query(models.Attendance)
        .filter(models.Attendance.student_id == student_id)
        .order_by(models.Attendance.created_at.desc())
        .all()
    )

def create_attendance(
    db: Session,
    *,
    student_id: int,
    lecturer_id: int,
    session_id: int,
    course_name: str,
    course_code: str,
    course_title: str,
    date_value,
    status: str = "present"
):
    attendance = models.Attendance(
        student_id=student_id,
        lecturer_id=lecturer_id,
        session_id=session_id,
        course_name=course_name,
        course_code=course_code,
        course_title=course_title,
        date=date_value,
        status=status
    )

    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance



# ----------------------------
# NEW: Attendance Session CRUD
# ----------------------------
def create_attendance_session(db: Session, session_in: schemas.AttendanceSessionCreate, lecturer_id:int):
    """Create a new class attendance session with a unique session code."""

    unique_code = f"S-{uuid.uuid4().hex[:6].upper()}"

    session = models.AttendanceSession(
        lecturer_id=lecturer_id,
        course_code=session_in.course_code,
        course_title=session_in.course_title,
        date=session_in.date,
        session_code=unique_code
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

def get_attendance_for_lecturer(db: Session, lecturer_id: int):
    return (
        db.query(models.Attendance)
        .filter(models.Attendance.lecturer_id == lecturer_id)
        .order_by(models.Attendance.created_at.desc())
        .all()
    )
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