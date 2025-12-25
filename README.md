📊 Smart Attendance System

A web-based Smart Attendance System designed to manage student attendance efficiently using a modern backend API and a lightweight frontend interface.

This project supports authentication, role-based dashboards, lecture session creation, and attendance tracking for educational institutions.

🚀 Features

🔐 Authentication & Authorization

JWT-based login system

Role separation (Admin / Lecturer / Student)

👨‍🏫 Lecturer Dashboard

Create lecture sessions

View attendance records

Manage assigned courses

👨‍🎓 Student Dashboard

View attendance history

Mark attendance for active sessions

🗄️ Database Management

SQLAlchemy ORM

Alembic migrations

🌐 REST API

Built with FastAPI

Swagger UI for testing

🎨 Frontend

HTML, CSS, Vanilla JavaScript
🛠️ Tech Stack
Backend

Python

FastAPI

SQLAlchemy

Alembic

JWT Authentication

SQLite / PostgreSQL

Frontend

HTML

CSS

JavaScript (Vanilla)

📁 Project Structure
attendance_app/
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   ├── routes/
│   │   └── utils/
│   └── alembic.ini
│
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── Dashboard.html
│   ├── css/
│   ├── js/
│   └── assets/
│
├── PROJECT_PROGRESS.md
└── README.md
⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/your-username/attendance_app.git
cd attendance_app

2️⃣ Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt


Create a .env file:

DATABASE_URL=sqlite:///./attendance.db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30


Run migrations:

alembic upgrade head


Start the server:

uvicorn app.main:app --reload


Backend will run at:

http://127.0.0.1:8000


Swagger UI:

http://127.0.0.1:8000/docs
3️⃣ Frontend Setup

Open the frontend files using Live Server or any static server:

frontend/
 ├── index.html
 ├── login.html
 └── Dashboard.html


Make sure the API_BASE URL in JS files matches the backend:

const API_BASE = "http://127.0.0.1:8000";

🔐 Authentication Flow

User registers or logs in

JWT token is returned

Token is stored in localStorage

Token is attached to API requests via Authorization header

🧪 Testing

Use Swagger UI for API testing

Use browser DevTools → Network tab for frontend debugging
🛡️ Security Notes

.env is ignored from GitHub

Passwords are hashed

JWT tokens are validated on protected routes

🧾 GitHub Best Practices
.gitignore (important)
__pycache__/
venv/
.env
*.db
*.pyc

Recommended Branches

main → stable production code

dev → active development

feature/* → new features

📌 Project Status

🚧 Active Development

See PROJECT_PROGRESS.md for:

Completed features

Pending tasks

Known issues

👤 Author

Official Vicks
Software Developer
