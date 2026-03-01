from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app import schemas, models
from app.database import get_db
from app.utils import security



router = APIRouter(
    prefix="/schools",
    tags=["School"]
)
@router.post("/", response_model=schemas.SchoolOut)
def create_school(
    school: schemas.SchoolCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(security.get_current_admin)
):
    # Check duplicate
    existing = db.query(models.School).filter(
        models.School.name == school.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="School already exists"
        )

    new_school = models.School(name=school.name)

    db.add(new_school)
    db.commit()
    db.refresh(new_school)

    return new_school

@router.get("/allSchools")
def list_schools(db: Session = Depends(get_db)):
    return db.query(models.School).all()