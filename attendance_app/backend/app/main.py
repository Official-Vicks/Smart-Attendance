"""
main.py
FastAPI entry point.

Provides:
- /auth/register/student
- /auth/register/lecturer
- /auth/login/student
- /auth/login/lecturer
- /attendance endpoints
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import engine, get_db
import datetime
from app.config import settings
from typing import List
from app.routes import students, lecturers, auth, attendance
from fastapi.openapi.utils import get_openapi


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    description="Backend for attendance system",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
         "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request

@app.get("/debug-auth")
def debug_auth(request: Request):
    return {
        "authorization_header": request.headers.get("authorization")
    }

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(lecturers.router)
app.include_router(attendance.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "timestamp": datetime.datetime.utcnow()}


@app.get("/")
def root():
    return {"message": f"Welcome to {settings.APP_NAME}"}


# =====================================================
# CUSTOM SWAGGER (OpenAPI) FOR JWT AUTH
# =====================================================

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version="1.0.0",
        description="Backend for attendance system",
        routes=app.routes,
    )

    # Add JWT Bearer Authentication
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Apply BearerAuth globally to all endpoints
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # <-- ACTIVATE CUSTOM SWAGGER
