import os
from dotenv import load_dotenv

load_dotenv()


def _normalize_db_url(url: str) -> str:
    # Render (and Heroku) hand out "postgres://..." but SQLAlchemy 2.x needs "postgresql://".
    if url and url.startswith('postgres://'):
        return url.replace('postgres://', 'postgresql://', 1)
    return url


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-only-change-in-production'
    SQLALCHEMY_DATABASE_URI = _normalize_db_url(os.environ.get('DATABASE_URL') or 'sqlite:///dtu_portal.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google OAuth Credentials (Get from Google Cloud Console)
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

    # App settings
    UNIVERSITY_NAME = os.environ.get('UNIVERSITY_NAME') or 'Delhi Technological University'
    UNIVERSITY_SHORT = os.environ.get('UNIVERSITY_SHORT') or 'DTU'
    EXAM_BRANCH_EMAIL = os.environ.get('EXAM_BRANCH_EMAIL') or 'examdtu@gmail.com'
