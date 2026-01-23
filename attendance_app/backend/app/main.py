"""
main.py
FastAPI entry point.

Provides:
- /auth endpoints
- /attendance endpoints
- /lecturer endpoints
- /student endpoints
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import datetime
from app.config import settings
from app.routes import students, lecturers, auth, attendance, admin_auth, admin
from fastapi.openapi.utils import get_openapi
from tests import test_attendance
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.models import Base
from app.database import engine
import os



app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    description="Backend for attendance system",
    version="1.0.0"
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(lecturers.router)
app.include_router(attendance.router)
app.include_router(test_attendance.router)
app.include_router(admin_auth.router)
app.include_router(admin.router)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# -------------------------------------------------
# 1️⃣ Serve uploads (specific path FIRST)
# -------------------------------------------------
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_DIR),
    name="uploads"
)

FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

app.mount(
    "/",
    StaticFiles(directory=FRONTEND_DIR, html=True),
    name="frontend"
)
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
