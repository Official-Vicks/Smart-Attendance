# backend/app/routes/auth.py

"""
auth.py
Handles authentication and registration for lecturers and students.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app import crud, schemas, models
from app.database import get_db
from app.utils import security
from app.config import settings
from typing import List

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# Lecturer Registration (unchanged signature but simplified)
@router.post("/register/lecturer", response_model=schemas.LecturerOut)
def register_lecturer(lecturer: schemas.LecturerCreate, db: Session = Depends(get_db)):
    """Register a new lecturer account"""
    existing = crud.lecturer_email_exists(db, lecturer.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Pass the Pydantic model to crud.create_lecturer (it will hash password)
    new_lecturer = crud.create_lecturer(db, lecturer)
    return new_lecturer


# Student Registration
@router.post("/register/student", response_model=schemas.StudentOut)
def register_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    """Register a new student account"""
    existing = crud.student_email_exists(db, student.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_student = crud.create_student(db, student)
    return new_student


# Lecturer login (separate route)
@router.post("/login/lecturer", response_model=schemas.Token)
def login_lecturer(payload: schemas.LecturerLogin, db: Session = Depends(get_db)):
    """
    Lecturer login endpoint.
    Accepts JSON: { email, password }
    """
    user = crud.authenticate_lecturer(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email, password, or non-existing account")

    #create JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"email": user.email, "role": "lecturer", "user_id": user.id},
        expires_delta=access_token_expires
    )
    return {
    "access_token": access_token,
    "token_type": "bearer",
    "user_id": user.id,
    "role": "lecturer",
    "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60}



# Student login (separate route)
@router.post("/login/student", response_model=schemas.Token)
def login_student(payload: schemas.StudentLogin, db: Session = Depends(get_db)):
    """
    Student login endpoint.
    Accepts JSON: { email, password }
    """
    user = crud.authenticate_student(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email, password or non-existing account")

    #create JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"email": user.email, "role": "student", "user_id": user.id},
        expires_delta=access_token_expires
    )
    return {
    "access_token": access_token,
    "token_type": "bearer",
    "user_id": user.id,
    "role": "student"
}
