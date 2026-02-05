"""
schemas.py
Pydantic models for Smart Attendance System.
Used for request validation and response serialization.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import datetime 
from datetime import date

# Admin schemas
class AdminCreate(BaseModel):
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


class LecturerOut(LecturerBase):
    id: int
    profile_image: Optional[str] = None

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
    profile_image: Optional[str] = None

    model_config = {"from_attributes": True}


class StudentLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class StudentLog(StudentLogin):
    id: int

    model_config = {"from_attributes": True}

class MyAttendanceOut(BaseModel):
    id: int
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
    date: datetime.date
    status: str = "present"


class AttendanceCreate(AttendanceBase):
    student_id: int
    lecturer_id: int
    course_id: int



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
    course_code:str
    course_title:str
    date:datetime.date


class AttendanceMarkCreate(BaseModel):
    session_id: int

class AttendanceSessionOut(BaseModel):
    id: int
    lecturer_id: int
    lecturer_name: str
    course_code: str
    course_title: str
    date: date
    session_code: str
    is_active: bool

    model_config = {"from_attributes": True}

class AttendanceOut(BaseModel):
    id: int
    student_id: int
    student_name: str
    lecturer_id: int
    lecturer_name: str
    session_id: int
    course_code: str
    course_title: str
    date: date
    status: str


    model_config = {"from_attributes": True}
