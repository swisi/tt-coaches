
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-65c7c9b3cd50436aae77309d09e45876'
    # Datenbank-URI (für Docker: kann in data/ Verzeichnis sein)
    db_path = os.environ.get('DATABASE_PATH', basedir)
    # Stelle sicher, dass das Verzeichnis existiert
    os.makedirs(db_path, exist_ok=True)
    # Wenn DATABASE_URL gesetzt ist, verwende es, sonst baue URI aus DATABASE_PATH
    # WICHTIG: SQLite benötigt 4 Slashes für absoluten Pfad: sqlite:////path/to/db.db
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        SQLALCHEMY_DATABASE_URI = db_url
    else:
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(db_path, "coaches.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings (kann über Umgebungsvariable überschrieben werden)
    upload_base = os.environ.get('UPLOAD_BASE', basedir)
    UPLOAD_FOLDER = os.path.join(upload_base, 'app', 'static', 'uploads', 'certificates')
    # Max Upload-Größe: Standard 500MB (für große Backup-Dateien)
    # Kann über MAX_CONTENT_LENGTH Umgebungsvariable überschrieben werden (in Bytes)
    max_content_length = os.environ.get('MAX_CONTENT_LENGTH')
    if max_content_length:
        MAX_CONTENT_LENGTH = int(max_content_length)
    else:
        MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB default (für Backup-Dateien)
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'zip', 'json'}  # Backup-Formate hinzugefügt
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Zitadel OAuth2/OIDC settings
    ZITADEL_ISSUER = os.environ.get('ZITADEL_ISSUER') or 'https://your-zitadel-instance.com'
    ZITADEL_CLIENT_ID = os.environ.get('ZITADEL_CLIENT_ID') or ''
    ZITADEL_CLIENT_SECRET = os.environ.get('ZITADEL_CLIENT_SECRET') or ''
    ZITADEL_REDIRECT_URI = os.environ.get('ZITADEL_REDIRECT_URI') or 'http://localhost:5000/auth/callback'
    # Management API URL (z.B. https://your-zitadel-instance.com)
    ZITADEL_MANAGEMENT_API_URL = os.environ.get('ZITADEL_MANAGEMENT_API_URL') or ''
    # Management API Token (Service Account Token mit Berechtigung zum Erstellen von Benutzern)
    ZITADEL_MANAGEMENT_API_TOKEN = os.environ.get('ZITADEL_MANAGEMENT_API_TOKEN') or ''
    # Standard-Rolle für neue Benutzer (optional, muss in Zitadel konfiguriert sein)
    ZITADEL_DEFAULT_ROLE = os.environ.get('ZITADEL_DEFAULT_ROLE') or 'coach'

