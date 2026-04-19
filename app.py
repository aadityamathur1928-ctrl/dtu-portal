import os
from flask import Flask, redirect, url_for
from config import Config
from extensions import db, login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    # Register blueprints
    from routes.auth import auth_bp
    from routes.student import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp, url_prefix='/student')

    # Root redirect
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    # Lightweight health check – used by the keep-warm cron.
    @app.route('/healthz')
    def healthz():
        return 'ok', 200

    # User loader
    from models import Student

    @login_manager.user_loader
    def load_user(user_id):
        return Student.query.get(int(user_id))

    # Create tables & seed data
    with app.app_context():
        db.create_all()
        seed_sample_data()

    return app


def seed_sample_data():
    """Seed the database with sample data for demo purposes."""
    from models import Student, Notice, ExamSchedule, Result
    from datetime import date

    # Seed notices
    if not Notice.query.first():
        notices = [
            Notice(
                title="End Semester Examination Schedule – Even Semester 2024-25 Released",
                content="The examination schedule for Even Semester 2024-25 has been officially released. "
                        "All students are advised to check their respective schedules carefully. "
                        "No re-scheduling of examinations will be entertained except in genuine cases with prior approval.",
                category="exam", is_important=True, posted_by="Controller of Examinations"
            ),
            Notice(
                title="Admit Card Download Now Open",
                content="Students appearing in Even Semester End Term Examinations 2024-25 can now download their "
                        "Admit Cards from the Student Portal. Students must carry a printed copy of their Admit Card "
                        "along with a valid college ID on all examination days.",
                category="admit_card", is_important=True, posted_by="Examination Branch"
            ),
            Notice(
                title="Odd Semester 2024 Results Declared",
                content="The results of End Term Examination (Odd Semester) 2024 have been declared. "
                        "Students may view their results on the portal. "
                        "For any discrepancy in result, please contact the Examination Branch within 15 days.",
                category="result", is_important=False, posted_by="Examination Branch"
            ),
            Notice(
                title="Re-evaluation / Rechecking Application – Last Date 30 April 2025",
                content="Students who wish to apply for re-evaluation or rechecking of their answer scripts for "
                        "Odd Semester 2024 examinations should submit their applications before 30 April 2025. "
                        "Applications submitted after the deadline will not be entertained.",
                category="general", is_important=False, posted_by="Examination Branch"
            ),
            Notice(
                title="University Closed – Public Holiday Notice",
                content="The University offices and Examination Branch will remain closed on account of public holidays. "
                        "All pending work will be addressed after the holidays resume.",
                category="holiday", is_important=False, posted_by="Administration"
            ),
        ]
        for n in notices:
            db.session.add(n)

    # Seed exam schedules
    if not ExamSchedule.query.first():
        exams = [
            ExamSchedule(subject_name="Engineering Mathematics – III", subject_code="MA201",
                         exam_date=date(2025, 5, 5), exam_time="9:00 AM", duration_hours=3,
                         venue="Block AB, Hall A", branch="CSE", semester=4,
                         session="Even 2024-25"),
            ExamSchedule(subject_name="Data Structures & Algorithms", subject_code="CS203",
                         exam_date=date(2025, 5, 7), exam_time="9:00 AM", duration_hours=3,
                         venue="Block AB, Hall B", branch="CSE", semester=4,
                         session="Even 2024-25"),
            ExamSchedule(subject_name="Computer Organization & Architecture", subject_code="CS205",
                         exam_date=date(2025, 5, 9), exam_time="9:00 AM", duration_hours=3,
                         venue="Block AB, Hall A", branch="CSE", semester=4,
                         session="Even 2024-25"),
            ExamSchedule(subject_name="Operating Systems", subject_code="CS207",
                         exam_date=date(2025, 5, 12), exam_time="9:00 AM", duration_hours=3,
                         venue="Block AB, Hall C", branch="CSE", semester=4,
                         session="Even 2024-25"),
            ExamSchedule(subject_name="Database Management Systems", subject_code="CS209",
                         exam_date=date(2025, 5, 14), exam_time="9:00 AM", duration_hours=3,
                         venue="Block AB, Hall A", branch="CSE", semester=4,
                         session="Even 2024-25"),
            ExamSchedule(subject_name="Probability & Statistics", subject_code="MA203",
                         exam_date=date(2025, 5, 16), exam_time="9:00 AM", duration_hours=3,
                         venue="Block AB, Hall B", branch="CSE", semester=4,
                         session="Even 2024-25"),
        ]
        for e in exams:
            db.session.add(e)

    # Seed demo student #1 – Aaditya Mathur (IT)
    if not Student.query.filter_by(roll_number="22/IT/01").first():
        student = Student(
            roll_number="22/IT/01",
            name="Aaditya Mathur",
            email="demo@dtu.ac.in",
            branch="Information Technology",
            programme="B.Tech",
            semester=8,
            year=4
        )
        student.set_password("nmke3391")
        db.session.add(student)
        db.session.flush()

        results = [
            Result(student_id=student.id, subject_code="CS101", subject_name="Programming Fundamentals",
                   internal_marks=28, external_marks=62, total_marks=90, max_marks=100,
                   grade="O", grade_points=10.0, credits=4, semester=1, year=2022),
            Result(student_id=student.id, subject_code="MA101", subject_name="Engineering Mathematics – I",
                   internal_marks=24, external_marks=58, total_marks=82, max_marks=100,
                   grade="A+", grade_points=9.0, credits=4, semester=1, year=2022),
            Result(student_id=student.id, subject_code="PH101", subject_name="Engineering Physics",
                   internal_marks=22, external_marks=55, total_marks=77, max_marks=100,
                   grade="A", grade_points=8.0, credits=4, semester=1, year=2022),
            Result(student_id=student.id, subject_code="EE101", subject_name="Basic Electrical Engineering",
                   internal_marks=20, external_marks=53, total_marks=73, max_marks=100,
                   grade="A", grade_points=8.0, credits=4, semester=1, year=2022),
            Result(student_id=student.id, subject_code="CS201", subject_name="Object Oriented Programming",
                   internal_marks=27, external_marks=65, total_marks=92, max_marks=100,
                   grade="O", grade_points=10.0, credits=4, semester=2, year=2023),
            Result(student_id=student.id, subject_code="MA201", subject_name="Engineering Mathematics – II",
                   internal_marks=25, external_marks=60, total_marks=85, max_marks=100,
                   grade="A+", grade_points=9.0, credits=4, semester=2, year=2023),
            Result(student_id=student.id, subject_code="CS203", subject_name="Digital Electronics",
                   internal_marks=23, external_marks=57, total_marks=80, max_marks=100,
                   grade="A+", grade_points=9.0, credits=4, semester=2, year=2023),
        ]
        for r in results:
            db.session.add(r)

    # Seed demo student #2 – Vishnu Singh Poonia (CO)
    if not Student.query.filter_by(roll_number="22/CO/504").first():
        student2 = Student(
            roll_number="22/CO/504",
            name="Vishnu Singh Poonia",
            email="vishnusinghpoonia_co22a8_20@dtu.ac.in",
            branch="Computer Engineering",
            programme="B.Tech",
            semester=8,
            year=4
        )
        student2.set_password("vishnu504")
        db.session.add(student2)
        db.session.flush()

        results2 = [
            Result(student_id=student2.id, subject_code="CO101", subject_name="Introduction to Computing",
                   internal_marks=26, external_marks=60, total_marks=86, max_marks=100,
                   grade="A+", grade_points=9.0, credits=4, semester=1, year=2022),
            Result(student_id=student2.id, subject_code="MA101", subject_name="Engineering Mathematics – I",
                   internal_marks=22, external_marks=54, total_marks=76, max_marks=100,
                   grade="A", grade_points=8.0, credits=4, semester=1, year=2022),
            Result(student_id=student2.id, subject_code="PH101", subject_name="Engineering Physics",
                   internal_marks=24, external_marks=58, total_marks=82, max_marks=100,
                   grade="A+", grade_points=9.0, credits=4, semester=1, year=2022),
            Result(student_id=student2.id, subject_code="CO201", subject_name="Data Structures",
                   internal_marks=25, external_marks=62, total_marks=87, max_marks=100,
                   grade="A+", grade_points=9.0, credits=4, semester=2, year=2023),
            Result(student_id=student2.id, subject_code="CO203", subject_name="Computer Organisation",
                   internal_marks=27, external_marks=63, total_marks=90, max_marks=100,
                   grade="O", grade_points=10.0, credits=4, semester=2, year=2023),
            Result(student_id=student2.id, subject_code="CO301", subject_name="Operating Systems",
                   internal_marks=21, external_marks=52, total_marks=73, max_marks=100,
                   grade="A", grade_points=8.0, credits=4, semester=3, year=2023),
            Result(student_id=student2.id, subject_code="CO303", subject_name="Database Management Systems",
                   internal_marks=23, external_marks=56, total_marks=79, max_marks=100,
                   grade="A", grade_points=8.0, credits=4, semester=3, year=2023),
        ]
        for r in results2:
            db.session.add(r)

    db.session.commit()


if __name__ == '__main__':
    # Local dev only. In production, gunicorn imports create_app directly.
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5050)),
        debug=os.environ.get('FLASK_DEBUG') == '1',
    )
