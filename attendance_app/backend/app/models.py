"""
models.py
Defines database tables for the Smart Attendance System.
Uses SQLAlchemy ORM with proper relationships.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
import datetime
import uuid

# ----------------------------
# Lecturer Model
# ----------------------------
class Lecturer(Base):
    __tablename__ = "lecturers"

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    course = Column(String)

    # Relationships
    students = relationship("Student", back_populates="lecturer")
    attendance_records = relationship("Attendance", back_populates="lecturer")
    courses = relationship("Course", back_populates="lecturer")
    attendance_sessions = relationship("AttendanceSession", back_populates="lecturer")


# ----------------------------
# Student Model
# ----------------------------
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    registration_number = Column(String, unique=True, nullable=False)
    department = Column(String)

    lecturer_id = Column(Integer, ForeignKey("lecturers.id"))
    lecturer = relationship("Lecturer", back_populates="students")

    attendance_records = relationship("Attendance", back_populates="student")


# ----------------------------
# Attendance Model
# ----------------------------
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    student_name = Column(String, nullable=False)
    lecturer_id = Column(Integer, ForeignKey("lecturers.id"), nullable=False)
    lecturer_name = Column(String, nullable=False)

    # NEW: session link
    session_id = Column(
        Integer,
        ForeignKey("attendance_sessions.id"),
        nullable=True,
        index=True
    )

    # Course snapshot fields
    course_code = Column(String, nullable=False)
    course_title = Column(String, nullable=False)

    date = Column(Date, nullable=False, index=True)
    status = Column(String, nullable=False, default="present")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    lecturer = relationship("Lecturer", back_populates="attendance_records")
    session = relationship("AttendanceSession")


# ----------------------------
# Course Model
# ----------------------------
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)

    lecturer_id = Column(Integer, ForeignKey("lecturers.id"), nullable=False)

    lecturer = relationship("Lecturer", back_populates="courses")


# ----------------------------
# NEW: Attendance Session Model
# ----------------------------
class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id = Column(Integer, primary_key=True, index=True)
    lecturer_id = Column(Integer, ForeignKey("lecturers.id"), nullable=False)
    lecturer_name = Column(String, nullable=False)

    course_code = Column(String, nullable=False)
    course_title = Column(String, nullable=False)

    date = Column(Date, nullable=False)

    session_code = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    closed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    lecturer = relationship("Lecturer", back_populates="attendance_sessions")
