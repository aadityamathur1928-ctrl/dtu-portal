from flask import Blueprint, render_template, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from models import ExamSchedule, Notice, Result
from utils.pdf_generator import generate_admit_card
import io
from datetime import date

student_bp = Blueprint('student', __name__)


# ── Dashboard ──────────────────────────────────────────────────────────────────

@student_bp.route('/dashboard')
@login_required
def dashboard():
    # Get upcoming exams for this student
    upcoming_exams = ExamSchedule.query.filter(
        ExamSchedule.exam_date >= date.today()
    ).filter(
        (ExamSchedule.branch == current_user.branch) |
        (ExamSchedule.branch == 'ALL') |
        (ExamSchedule.semester == current_user.semester)
    ).order_by(ExamSchedule.exam_date).limit(3).all()

    # Latest notices
    latest_notices = Notice.query.order_by(Notice.date_posted.desc()).limit(5).all()

    # Recent results
    recent_results = Result.query.filter_by(
        student_id=current_user.id
    ).order_by(Result.semester.desc()).limit(5).all()

    # Stats
    total_exams = ExamSchedule.query.filter(
        ExamSchedule.exam_date >= date.today()
    ).filter(
        (ExamSchedule.semester == current_user.semester) |
        (ExamSchedule.branch == current_user.branch)
    ).count()

    important_notices = Notice.query.filter_by(is_important=True).count()
    cgpa = current_user.get_cgpa()

    return render_template(
        'student/dashboard.html',
        upcoming_exams=upcoming_exams,
        latest_notices=latest_notices,
        recent_results=recent_results,
        total_exams=total_exams,
        important_notices=important_notices,
        cgpa=cgpa
    )


# ── Notifications (Examination Branch legacy page replica) ─────────────────────

@student_bp.route('/notifications')
@login_required
def notifications():
    return render_template('student/notifications.html')


# ── Course Registration (replica view) ─────────────────────────────────────────

@student_bp.route('/course-registration')
@login_required
def course_registration():
    return render_template('student/course_registration.html')


# ── Fee Status ─────────────────────────────────────────────────────────────────

@student_bp.route('/fee-status')
@login_required
def fee_status():
    return render_template('student/fee_status.html')


# ── Backlogs ───────────────────────────────────────────────────────────────────

@student_bp.route('/backlogs')
@login_required
def backlogs():
    return render_template('student/backlogs.html')


# ── Exam Schedule ──────────────────────────────────────────────────────────────

@student_bp.route('/exam-schedule')
@login_required
def exam_schedule():
    exams = ExamSchedule.query.filter(
        (ExamSchedule.branch == current_user.branch) |
        (ExamSchedule.branch == 'ALL') |
        (ExamSchedule.semester == current_user.semester)
    ).order_by(ExamSchedule.exam_date).all()

    # Group by semester/session
    sessions = {}
    for exam in exams:
        key = exam.session or 'General'
        sessions.setdefault(key, []).append(exam)

    today = date.today()
    return render_template(
        'student/exam_schedule.html',
        exams=exams,
        sessions=sessions,
        today=today
    )


# ── Admit Card ─────────────────────────────────────────────────────────────────

@student_bp.route('/admit-card')
@login_required
def admit_card():
    exams = ExamSchedule.query.filter(
        ExamSchedule.exam_date >= date.today()
    ).filter(
        (ExamSchedule.branch == current_user.branch) |
        (ExamSchedule.branch == 'ALL') |
        (ExamSchedule.semester == current_user.semester)
    ).order_by(ExamSchedule.exam_date).all()

    return render_template('student/admit_card.html', exams=exams)


@student_bp.route('/admit-card/download')
@login_required
def download_admit_card():
    exams = ExamSchedule.query.filter(
        ExamSchedule.exam_date >= date.today()
    ).filter(
        (ExamSchedule.branch == current_user.branch) |
        (ExamSchedule.branch == 'ALL') |
        (ExamSchedule.semester == current_user.semester)
    ).order_by(ExamSchedule.exam_date).all()

    pdf_buffer = generate_admit_card(current_user, exams)
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"AdmitCard_{current_user.roll_number.replace('/', '-')}.pdf"
    )


# ── Notices ────────────────────────────────────────────────────────────────────

@student_bp.route('/notices')
@login_required
def notices():
    category = None
    query = Notice.query.order_by(Notice.is_important.desc(), Notice.date_posted.desc())
    all_notices = query.all()

    # Group by category
    by_category = {}
    for n in all_notices:
        by_category.setdefault(n.category, []).append(n)

    important = Notice.query.filter_by(is_important=True).order_by(Notice.date_posted.desc()).all()

    return render_template(
        'student/notices.html',
        notices=all_notices,
        by_category=by_category,
        important=important
    )


# ── Results ────────────────────────────────────────────────────────────────────

@student_bp.route('/results')
@login_required
def results():
    all_results = Result.query.filter_by(
        student_id=current_user.id
    ).order_by(Result.semester, Result.subject_code).all()

    # Group by semester
    by_semester = {}
    for r in all_results:
        by_semester.setdefault(r.semester, []).append(r)

    # Calculate SGPA per semester
    sgpa_by_sem = {}
    for sem, sem_results in by_semester.items():
        total_gp = sum((r.grade_points or 0) * (r.credits or 4) for r in sem_results)
        total_credits = sum(r.credits or 4 for r in sem_results)
        sgpa_by_sem[sem] = round(total_gp / total_credits, 2) if total_credits else 0

    # Overall CGPA
    cgpa = current_user.get_cgpa()

    return render_template(
        'student/results.html',
        by_semester=by_semester,
        sgpa_by_sem=sgpa_by_sem,
        cgpa=cgpa,
        all_results=all_results
    )
