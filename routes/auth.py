import json
import requests
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length
from extensions import db
from models import Student

auth_bp = Blueprint('auth', __name__)


class LoginForm(FlaskForm):
    roll_number = StringField('Roll Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    remember_me = BooleanField('Remember Me')


class FindEmailForm(FlaskForm):
    roll_number = StringField('Roll Number', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    roll_number = StringField('Roll Number', validators=[DataRequired()])
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    branch = StringField('Branch', validators=[DataRequired()])
    semester = StringField('Semester', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])


# ── Login ──────────────────────────────────────────────────────────────────────

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))

    form = LoginForm()
    find_email_form = FindEmailForm()
    found_email = None

    if form.validate_on_submit():
        roll = form.roll_number.data.strip().upper()
        student = Student.query.filter_by(roll_number=roll).first()
        if student and student.check_password(form.password.data):
            login_user(student, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash(f'Welcome back, {student.name.split()[0]}!', 'success')
            return redirect(next_page or url_for('student.dashboard'))
        flash('Invalid roll number or password. Please try again.', 'danger')

    return render_template('auth/login.html', form=form,
                           find_email_form=find_email_form,
                           found_email=found_email)


@auth_bp.route('/find-email', methods=['POST'])
def find_email():
    form = FindEmailForm()
    login_form = LoginForm()
    found_email = None
    if form.validate_on_submit():
        roll = form.roll_number.data.strip().upper()
        student = Student.query.filter_by(roll_number=roll).first()
        if student:
            found_email = student.email
            flash(f'Registered email for {roll}: {student.email}', 'info')
        else:
            flash(f'No student found with roll number {roll}.', 'warning')
    return render_template('auth/login.html', form=login_form,
                           find_email_form=form,
                           found_email=found_email)


# ── Register ───────────────────────────────────────────────────────────────────

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        # Check duplicates
        if Student.query.filter_by(email=form.email.data.lower()).first():
            flash('An account with this email already exists.', 'danger')
            return render_template('auth/register.html', form=form)
        if Student.query.filter_by(roll_number=form.roll_number.data.upper()).first():
            flash('A student with this Roll Number already exists.', 'danger')
            return render_template('auth/register.html', form=form)

        student = Student(
            roll_number=form.roll_number.data.upper(),
            name=form.name.data,
            email=form.email.data.lower(),
            branch=form.branch.data,
            semester=int(form.semester.data)
        )
        student.set_password(form.password.data)
        db.session.add(student)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


# ── Google OAuth ───────────────────────────────────────────────────────────────

@auth_bp.route('/auth/google')
def google_login():
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    if not client_id:
        flash('Google login is not configured. Please use email/password.', 'warning')
        return redirect(url_for('auth.login'))

    google_provider_cfg = requests.get(current_app.config['GOOGLE_DISCOVERY_URL']).json()
    authorization_endpoint = google_provider_cfg['authorization_endpoint']

    redirect_uri = url_for('auth.google_callback', _external=True)
    scope = 'openid email profile'

    auth_url = (
        f"{authorization_endpoint}?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope}"
    )
    return redirect(auth_url)


@auth_bp.route('/auth/google/callback')
def google_callback():
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')

    if not client_id:
        flash('Google login is not configured.', 'warning')
        return redirect(url_for('auth.login'))

    code = request.args.get('code')
    google_provider_cfg = requests.get(current_app.config['GOOGLE_DISCOVERY_URL']).json()
    token_endpoint = google_provider_cfg['token_endpoint']

    # Exchange code for token
    token_response = requests.post(
        token_endpoint,
        data={
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': url_for('auth.google_callback', _external=True),
            'grant_type': 'authorization_code',
        }
    )
    token_json = token_response.json()
    access_token = token_json.get('access_token')

    # Get user info
    userinfo_endpoint = google_provider_cfg['userinfo_endpoint']
    userinfo = requests.get(
        userinfo_endpoint,
        headers={'Authorization': f'Bearer {access_token}'}
    ).json()

    google_id = userinfo.get('sub')
    email = userinfo.get('email')
    name = userinfo.get('name')
    picture = userinfo.get('picture')

    student = Student.query.filter_by(google_id=google_id).first()
    if not student:
        student = Student.query.filter_by(email=email).first()
        if student:
            student.google_id = google_id
            student.profile_pic = picture
        else:
            # Auto-register
            student = Student(
                roll_number=f"G-{google_id[:8].upper()}",
                name=name,
                email=email,
                google_id=google_id,
                profile_pic=picture,
                branch="Not Set",
                semester=1
            )
            db.session.add(student)

    db.session.commit()
    login_user(student)
    flash(f'Welcome, {name.split()[0]}! You are logged in via Google.', 'success')
    return redirect(url_for('student.dashboard'))


# ── Logout ─────────────────────────────────────────────────────────────────────

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
