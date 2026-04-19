# DTU Examination Portal

A full-featured student examination portal inspired by reg-exam.dtu.ac.in, built with **Flask + PostgreSQL**.

---

## Features

| Feature | Details |
|---|---|
| Student Login | Email/password + Google OAuth |
| Student Registration | Self-registration with roll number |
| Dashboard | Upcoming exams, notices, CGPA overview |
| Exam Schedule | Complete timetable with status indicators |
| Admit Card | Live preview + PDF download (ReportLab) |
| Notices | Filterable announcements by category |
| Results | Semester-wise results with SGPA & CGPA |
| Responsive UI | Mobile-friendly sidebar layout |

---

## Tech Stack

- **Backend**: Python 3.10+ / Flask 3.0
- **Database**: PostgreSQL (via SQLAlchemy)
- **Auth**: Flask-Login + Google OAuth (via requests)
- **PDF**: ReportLab
- **Frontend**: HTML/CSS/JS (Jinja2 templates, Sora + DM Sans fonts)

---

## Prerequisites

- Python 3.10 or higher
- PostgreSQL installed and running
- (Optional) Google Cloud project for Google OAuth

---

## Quick Setup

### 1. Clone / extract the project

```bash
cd dtu_portal
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL database

```sql
-- In psql or pgAdmin, run:
CREATE DATABASE dtu_portal;
CREATE USER portal_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE dtu_portal TO portal_user;
```

### 5. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in:

```env
SECRET_KEY=any-long-random-string
DATABASE_URL=postgresql://portal_user:yourpassword@localhost/dtu_portal
GOOGLE_CLIENT_ID=         # optional – leave blank to skip Google login
GOOGLE_CLIENT_SECRET=     # optional
```

### 6. Run the app

```bash
python app.py
```

The app will:
- Create all database tables automatically
- Seed demo data (notices, exam schedule, demo student)
- Start the server at `http://localhost:5000`

### 7. Login with demo credentials

```
Email:    demo@dtu.ac.in
Password: nmke3391
```

---

## Google OAuth Setup (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project → **APIs & Services** → **Credentials**
3. Click **Create Credentials** → **OAuth 2.0 Client ID**
4. Application type: **Web Application**
5. Add Authorized Redirect URI:
   - Development: `http://localhost:5000/auth/google/callback`
   - Production: `https://yourdomain.com/auth/google/callback`
6. Copy **Client ID** and **Client Secret** into your `.env`

---

## Project Structure

```
dtu_portal/
├── app.py                  # App factory + DB seeding
├── config.py               # Configuration from .env
├── extensions.py           # SQLAlchemy + LoginManager
├── models.py               # Student, ExamSchedule, Notice, Result
├── requirements.txt
├── .env.example
│
├── routes/
│   ├── auth.py             # Login, Register, Google OAuth, Logout
│   └── student.py          # Dashboard, Schedule, Admit Card, Notices, Results
│
├── utils/
│   └── pdf_generator.py    # ReportLab admit card PDF
│
├── templates/
│   ├── base.html           # Sidebar layout shell
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   └── student/
│       ├── dashboard.html
│       ├── exam_schedule.html
│       ├── admit_card.html
│       ├── notices.html
│       └── results.html
│
└── static/
    ├── css/style.css
    └── js/main.js
```

---

## Adding Real Data

To populate real exam schedules and results, use the Flask shell:

```bash
python -c "
from app import create_app
from extensions import db
from models import ExamSchedule, Notice, Result
from datetime import date

app = create_app()
with app.app_context():
    exam = ExamSchedule(
        subject_name='Software Engineering',
        subject_code='CS301',
        exam_date=date(2025, 5, 20),
        exam_time='9:00 AM',
        duration_hours=3,
        venue='Block AB, Hall A',
        branch='CSE',
        semester=6,
        session='Even 2024-25'
    )
    db.session.add(exam)
    db.session.commit()
    print('Added!')
"
```

---

## Deployment (Production)

### Using Gunicorn + Nginx

```bash
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

Then configure Nginx to proxy requests to port 8000.

### Environment for Production

```env
SECRET_KEY=long-random-production-key
DATABASE_URL=postgresql://user:pass@localhost/dtu_portal
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

---

## Customizing for a Different University

Edit `config.py`:

```python
UNIVERSITY_NAME = "Your University Name"
UNIVERSITY_SHORT = "YUN"
EXAM_BRANCH_EMAIL = "exam@youruniversity.ac.in"
```

Or set these in your `.env` file.

---

## License

Built for educational/institutional use. Customize freely.
