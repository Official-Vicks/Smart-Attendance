"""
schemas.py
Pydantic models for Smart Attendance System.
Used for request validation and response serialization.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import datetime

# ----------------------------
# LECTURER SCHEMAS
# ----------------------------
class LecturerBase(BaseModel):
    full_name: str
    email: EmailStr
    course: Optional[str] = None


class LecturerCreate(LecturerBase):
    password: str = Field(..., min_length=6)


class LecturerOut(LecturerBase):
    id: int

    model_config = {"from_attributes": True}


class LecturerLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class LecturerLog(LecturerLogin):
    id: int

    model_config = {"from_attributes": True}


# ----------------------------
# STUDENT SCHEMAS
# ----------------------------
class StudentBase(BaseModel):
    full_name: str
    email: EmailStr
    registration_number: str
    department: Optional[str] = None


class StudentCreate(StudentBase):
    password: str = Field(..., min_length=6)


class StudentOut(StudentBase):
    id: int

    model_config = {"from_attributes": True}


class StudentLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class StudentLog(StudentLogin):
    id: int

    model_config = {"from_attributes": True}


# ----------------------------
# ATTENDANCE SCHEMAS
# ----------------------------
class AttendanceBase(BaseModel):
    date: datetime.date
    status: str = "present"


class AttendanceCreate(AttendanceBase):
    student_id: int
    lecturer_id: int
    course_id: int


class AttendanceOut(AttendanceBase):
    id: int
    student_id: int
    lecturer_id: int
    lecturer_name: Optional[str] = None
    course: Optional[str] = None
    status: str
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


# ----------------------------
# TOKEN & AUTH
# ----------------------------
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: str


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None


# ----------------------------
# RESPONSE
# ----------------------------
class Message(BaseModel):
    message: str


# ----------------------------
# NEW: Attendance Session Schemas (Phase 2)
# ----------------------------
class AttendanceSessionCreate(BaseModel):
    course_code: str
    course_title: str
    date: datetime.date


class AttendanceSessionOut(BaseModel):
    id: int
    lecturer_id: int
    course_code: str
    course_title: str
    date: datetime.date
    session_code: str
    created_at: datetime.datetime

    model_config = {"from_attributes": True}