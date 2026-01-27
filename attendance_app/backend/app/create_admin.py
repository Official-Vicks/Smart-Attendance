from app.database import SessionLocal
from app import models
from app.utils.security import get_password_hash

db = SessionLocal()

email = "chidieberevictory218@gmail.com"
password = "Chidiebere123#"

existing = db.query(models.Admin).filter(models.Admin.email == email).first()

if existing:
    print("Admin already exists")
else:
    admin = models.Admin(
        email=email,
        hashed_password=get_password_hash(password),
        is_superadmin=True
    )
    db.add(admin)
    db.commit()
    print("Admin created successfully")
