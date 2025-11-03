"""
Konfigurationsdatei für die Flask-Anwendung
"""
import os
from pathlib import Path

# Basis-Verzeichnis der Anwendung
basedir = Path(__file__).parent.absolute()

class Config:
    """Basis-Konfiguration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-ändere-in-produktion'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://thuntig_coach:L4K-yqZRjn9jhCVDppUV@thuntig.mysql.db.hostpoint.ch/thuntig_coaches?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Upload-Konfiguration
    UPLOAD_FOLDER = basedir / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    
    # Verzeichnisse für Uploads
    CERTIFICATES_FOLDER = UPLOAD_FOLDER / 'certificates'
    CV_FOLDER = UPLOAD_FOLDER / 'cv'
    PROFILE_IMAGES_FOLDER = UPLOAD_FOLDER / 'profile_images'
    
    @staticmethod
    def init_app(app):
        """Initialisiere Upload-Verzeichnisse"""
        Config.UPLOAD_FOLDER.mkdir(exist_ok=True)
        Config.CERTIFICATES_FOLDER.mkdir(exist_ok=True)
        Config.CV_FOLDER.mkdir(exist_ok=True)
        Config.PROFILE_IMAGES_FOLDER.mkdir(exist_ok=True)

