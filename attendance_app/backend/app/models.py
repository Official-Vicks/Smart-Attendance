"""
models.py
Defines database tables for the Smart Attendance System.
Uses SQLAlchemy ORM with proper relationships.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import datetime
import uuid

#---------------------------
# Admin Model
#---------------------------
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# -----------------------------
# School model
# -----------------------------
class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(225), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    students = relationship("Student", back_populates="school", cascade="all, delete")
    lecturers = relationship("Lecturer", back_populates="school", cascade="all, delete")
    courses = relationship("Course", back_populates="school", cascade="all, delete")
    attendance_records = relationship("Attendance", back_populates="school", cascade="all, delete")
    attendance_sessions = relationship("AttendanceSession", back_populates="school", cascade="all, delete")

# ----------------------------
# Lecturer Model
# ----------------------------
class Lecturer(Base):
    __tablename__ = "lecturers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(225), nullable=False)
    email = Column(String(225), unique=True, nullable=False)
    hashed_password = Column(String(225), nullable=False)
    course = Column(String(225))
    profile_image = Column(String(225), nullable=True)
    is_active = Column(Boolean, default=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)


    # Relationships
    students = relationship("Student", back_populates="lecturer")
    attendance_records = relationship("Attendance", back_populates="lecturer")
    courses = relationship("Course", back_populates="lecturer")
    attendance_sessions = relationship("AttendanceSession", back_populates="lecturer")
    school = relationship("School", back_populates="lecturers")


# ----------------------------
# Student Model
# ----------------------------
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(225), nullable=False)
    email = Column(String(225), unique=True, nullable=False)
    hashed_password = Column(String(225), nullable=False)
    registration_number = Column(String(225), unique=True, nullable=False)
    department = Column(String(225))
    profile_image = Column(String(225), nullable=True)
    is_active = Column(Boolean, default=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)


    lecturer_id = Column(Integer, ForeignKey("lecturers.id"))
    lecturer = relationship("Lecturer", back_populates="students")
    school = relationship("School", back_populates="students")
    attendance_records = relationship("Attendance", back_populates="student")


# ----------------------------
# Attendance Model
# ----------------------------
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    student_name = Column(String(225), nullable=False)
    lecturer_id = Column(Integer, ForeignKey("lecturers.id"), nullable=False)
    lecturer_name = Column(String(225), nullable=False)

    # NEW: session link
    session_id = Column(
        Integer,
        ForeignKey("attendance_sessions.id"),
        nullable=True,
        index=True
    )

    # Course snapshot fields
    course_code = Column(String(225), nullable=False)
    course_title = Column(String(225), nullable=False)

    date = Column(Date, nullable=False, index=True)
    status = Column(String(225), nullable=False, default="present")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)

    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    school = relationship("School", back_populates="attendance_records")
    lecturer = relationship("Lecturer", back_populates="attendance_records")
    session = relationship("AttendanceSession")


# ----------------------------
# Course Model
# ----------------------------
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(225), nullable=False)
    code = Column(String(225), unique=True, nullable=False)

    lecturer_id = Column(Integer, ForeignKey("lecturers.id"), nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)

    lecturer = relationship("Lecturer", back_populates="courses")
    school = relationship("School", back_populates="courses")


# ----------------------------
# NEW: Attendance Session Model
# ----------------------------
class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id = Column(Integer, primary_key=True, index=True)
    lecturer_id = Column(Integer, ForeignKey("lecturers.id"), nullable=False)
    lecturer_name = Column(String(225), nullable=False)

    course_code = Column(String(225), nullable=False)
    course_title = Column(String(225), nullable=False)

    date = Column(Date, nullable=False)

    session_code = Column(String(225), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    closed_at = Column(DateTime, nullable=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lecturer = relationship("Lecturer", back_populates="attendance_sessions")
    school = relationship("School", back_populates="attendance_sessions")