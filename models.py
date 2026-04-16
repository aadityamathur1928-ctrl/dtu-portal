from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class Student(UserMixin, db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    branch = db.Column(db.String(50))
    programme = db.Column(db.String(20), default='B.Tech')
    semester = db.Column(db.Integer)
    year = db.Column(db.Integer)
    google_id = db.Column(db.String(100), unique=True)
    profile_pic = db.Column(db.String(300))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    results = db.relationship('Result', backref='student', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def get_cgpa(self):
        if not self.results:
            return None
        total_points = sum(r.grade_points or 0 for r in self.results)
        return round(total_points / len(self.results), 2) if self.results else None

    def __repr__(self):
        return f'<Student {self.roll_number}>'


class ExamSchedule(db.Model):
    __tablename__ = 'exam_schedules'

    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(150), nullable=False)
    subject_code = db.Column(db.String(20), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)
    exam_time = db.Column(db.String(20), nullable=False)
    duration_hours = db.Column(db.Integer, default=3)
    venue = db.Column(db.String(100))
    branch = db.Column(db.String(50))  # CSE, ECE, ME, etc. | 'ALL' for all branches
    semester = db.Column(db.Integer)
    exam_type = db.Column(db.String(30), default='End Semester')
    session = db.Column(db.String(30))  # e.g. "Even 2024-25"

    def __repr__(self):
        return f'<Exam {self.subject_code} - {self.exam_date}>'


class Notice(db.Model):
    __tablename__ = 'notices'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50), default='general')
    # categories: general | exam | admit_card | result | holiday | urgent
    is_important = db.Column(db.Boolean, default=False)
    attachment_url = db.Column(db.String(300))
    posted_by = db.Column(db.String(100), default='Examination Branch')

    def __repr__(self):
        return f'<Notice {self.title[:30]}>'


class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_code = db.Column(db.String(20), nullable=False)
    subject_name = db.Column(db.String(150), nullable=False)
    internal_marks = db.Column(db.Float)
    external_marks = db.Column(db.Float)
    total_marks = db.Column(db.Float)
    max_marks = db.Column(db.Float, default=100)
    grade = db.Column(db.String(5))
    grade_points = db.Column(db.Float)
    credits = db.Column(db.Integer, default=4)
    semester = db.Column(db.Integer)
    year = db.Column(db.Integer)
    exam_type = db.Column(db.String(30), default='End Semester')
    result_status = db.Column(db.String(10), default='Pass')  # Pass / Fail / Withheld

    def __repr__(self):
        return f'<Result {self.subject_code} - {self.grade}>'
