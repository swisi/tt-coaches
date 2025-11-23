
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-65c7c9b3cd50436aae77309d09e45876'
    # Datenbank-URI (für Docker: kann in data/ Verzeichnis sein)
    db_path = os.environ.get('DATABASE_PATH', basedir)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(db_path, "coaches.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings (kann über Umgebungsvariable überschrieben werden)
    upload_base = os.environ.get('UPLOAD_BASE', basedir)
    UPLOAD_FOLDER = os.path.join(upload_base, 'app', 'static', 'uploads', 'certificates')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

