"""
schemas.py
Pydantic models for Smart Attendance System.
Used for request validation and response serialization.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime
import uuid

# Admin schemas
class AdminCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str = Field(..., min_length=6)

# --------------------------
# Shared by both roles
# --------------------------
class ChangePassword(BaseModel):
    current_password: str
    new_password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
# ----------------------------
# LECTURER SCHEMAS
# ----------------------------
class LecturerBase(BaseModel):
    full_name: str
    email: EmailStr
    course: Optional[str] = None


class LecturerCreate(LecturerBase):
    password: str = Field(..., min_length=6)
    school_name: str


class LecturerOut(LecturerBase):
    id: uuid.UUID
    profile_image: Optional[str] = None
    school_id: uuid.UUID

    model_config = {"from_attributes": True}


class LecturerLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class LecturerLog(LecturerLogin):
    id: uuid.UUID

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
    school_name: str


class StudentOut(StudentBase):
    id: uuid.UUID
    profile_image: Optional[str] = None
    school_id: uuid.UUID

    model_config = {"from_attributes": True}


class StudentLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class StudentLog(StudentLogin):
    id: uuid.UUID

    model_config = {"from_attributes": True}

class MyAttendanceOut(BaseModel):
    id: uuid.UUID
    date: date
    status: str
    course_title: str
    course_code: str
    lecturer_name: str

    model_config = {"from_attributes": True}
# ----------------------------
# ATTENDANCE SCHEMAS
# ----------------------------
class AttendanceBase(BaseModel):
    date: date
    status: str = "present"


class AttendanceCreate(AttendanceBase):
    student_id: uuid.UUID
    lecturer_id: uuid.UUID
    course_id: uuid.UUID



# ----------------------------
# TOKEN & AUTH
# ----------------------------
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: uuid.UUID
    role: str 
    school_id: uuid.UUID


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
    course_code:str
    course_title:str
    date:date


class AttendanceMarkCreate(BaseModel):
    session_id: uuid.UUID

class AttendanceSessionOut(BaseModel):
    id: uuid.UUID
    lecturer_id: uuid.UUID
    lecturer_name: str
    course_code: str
    course_title: str
    date: date
    session_code: str
    is_active: bool

    model_config = {"from_attributes": True}

class AttendanceOut(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    lecturer_id: uuid.UUID
    lecturer_name: str
    session_id: uuid.UUID
    course_code: str
    course_title: str
    date: date
    status: str

    model_config = {"from_attributes": True}

class SchoolCreate(BaseModel):
    name: str

class SchoolOut(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}