"""
models.py
Defines database tables for the Smart Attendance System.
Uses SQLAlchemy ORM with proper relationships.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

#---------------------------
# Admin Model
#---------------------------
class Admin(Base):
    __tablename__ = "admins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(225), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    students = relationship("Student", back_populates="school", cascade="all, delete-orphan")
    lecturers = relationship("Lecturer", back_populates="school", cascade="all, delete-orphan")
    courses = relationship("Course", back_populates="school", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="school", cascade="all, delete-orphan")
    attendance_sessions = relationship("AttendanceSession", back_populates="school", cascade="all, delete-orphan")

# ----------------------------
# Lecturer Model
# ----------------------------
class Lecturer(Base):
    __tablename__ = "lecturers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    full_name = Column(String(225), nullable=False)
    email = Column(String(225), unique=True, nullable=False)
    hashed_password = Column(String(225), nullable=False)
    course = Column(String(225))
    profile_image = Column(String(225), nullable=True)
    is_active = Column(Boolean, default=True)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)


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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    full_name = Column(String(225), nullable=False)
    email = Column(String(225), unique=True, nullable=False)
    hashed_password = Column(String(225), nullable=False)
    registration_number = Column(String(225), unique=True, nullable=False)
    department = Column(String(225))
    profile_image = Column(String(225), nullable=True)
    is_active = Column(Boolean, default=True)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)


    lecturer_id = Column(UUID(as_uuid=True), ForeignKey("lecturers.id", ondelete="CASCADE"), index=True)
    lecturer = relationship("Lecturer", back_populates="students")
    school = relationship("School", back_populates="students")
    attendance_records = relationship("Attendance", back_populates="student")


# ----------------------------
# Attendance Model
# ----------------------------
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    student_name = Column(String(225), nullable=False)
    lecturer_id = Column(UUID(as_uuid=True), ForeignKey("lecturers.id", ondelete="CASCADE"), nullable=False, index=True)
    lecturer_name = Column(String(225), nullable=False)

    # NEW: session link
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("attendance_sessions.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Course snapshot fields
    course_code = Column(String(225), nullable=False)
    course_title = Column(String(225), nullable=False)

    date = Column(Date, nullable=False, index=True)
    status = Column(String(225), nullable=False, default="present")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)

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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(225), nullable=False)
    code = Column(String(225), unique=True, nullable=False)

    lecturer_id = Column(UUID(as_uuid=True), ForeignKey("lecturers.id", ondelete="CASCADE"), nullable=False, index=True)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)

    lecturer = relationship("Lecturer", back_populates="courses")
    school = relationship("School", back_populates="courses")


# ----------------------------
# NEW: Attendance Session Model
# ----------------------------
class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    lecturer_id = Column(UUID(as_uuid=True), ForeignKey("lecturers.id", ondelete="CASCADE"), nullable=False, index=True)
    lecturer_name = Column(String(225), nullable=False)

    course_code = Column(String(225), nullable=False)
    course_title = Column(String(225), nullable=False)

    date = Column(Date, nullable=False)

    session_code = Column(String(225), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    closed_at = Column(DateTime, nullable=True)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lecturer = relationship("Lecturer", back_populates="attendance_sessions")
    school = relationship("School", back_populates="attendance_sessions")