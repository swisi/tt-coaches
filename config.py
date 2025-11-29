
import os
from datetime import timedelta

# Lade Umgebungsvariablen aus .env Datei (falls vorhanden)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv nicht installiert, ignoriere
    pass

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-65c7c9b3cd50436aae77309d09e45876'
    # Datenbank-URI (für Docker: kann in data/ Verzeichnis sein)
    _db_path_env = os.environ.get('DATABASE_PATH', basedir)
    # Stelle sicher, dass das Verzeichnis existiert (nur wenn möglich)
    db_path = basedir  # Standard: basedir
    try:
        # Versuche das Verzeichnis aus der Umgebungsvariable zu erstellen
        os.makedirs(_db_path_env, exist_ok=True)
        db_path = _db_path_env
    except (OSError, PermissionError):
        # Falls das Verzeichnis nicht erstellt werden kann (z.B. read-only filesystem),
        # verwende basedir als Fallback
        try:
            os.makedirs(basedir, exist_ok=True)
            db_path = basedir
        except (OSError, PermissionError):
            pass  # Ignoriere Fehler, wenn auch das nicht funktioniert
    # Wenn DATABASE_URL gesetzt ist, verwende es, sonst baue URI aus DATABASE_PATH
    # WICHTIG: SQLite benötigt 4 Slashes für absoluten Pfad: sqlite:////path/to/db.db
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        # Prüfe, ob DATABASE_URL einen Docker-Pfad enthält, der lokal nicht funktioniert
        if db_url.startswith('sqlite:///') and '/app/' in db_url:
            # Versuche zu prüfen, ob der Pfad lokal existiert/beschreibbar ist
            db_file_path = db_url.replace('sqlite:///', '').replace('sqlite:////', '')
            db_dir = os.path.dirname(db_file_path)
            # Wenn das Verzeichnis nicht existiert oder nicht beschreibbar ist, verwende Fallback
            if not os.path.exists(db_dir) or not os.access(db_dir, os.W_OK):
                # Fallback: Verwende lokales data/ Verzeichnis
                data_dir = os.path.join(basedir, "data")
                os.makedirs(data_dir, exist_ok=True)
                db_file_path = os.path.join(data_dir, "coaches.db")
                SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_file_path}'
            else:
                SQLALCHEMY_DATABASE_URI = db_url
        else:
            SQLALCHEMY_DATABASE_URI = db_url
    else:
        db_file_path = os.path.join(db_path, "coaches.db")
        # Für absolute Pfade benötigt SQLite 4 Slashes (sqlite:////), für relative 3 (sqlite:///)
        # os.path.join gibt bereits absolute Pfade mit führendem / zurück
        if os.path.isabs(db_file_path):
            # Für absolute Pfade: sqlite://// (4 Slashes) - der Pfad beginnt bereits mit /
            SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_file_path}'
        else:
            SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_file_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings (kann über Umgebungsvariable überschrieben werden)
    _upload_base_env = os.environ.get('UPLOAD_BASE', basedir)
    upload_base = basedir  # Standard: basedir
    try:
        # Versuche das Verzeichnis aus der Umgebungsvariable zu verwenden
        os.makedirs(_upload_base_env, exist_ok=True)
        upload_base = _upload_base_env
    except (OSError, PermissionError):
        # Falls das Verzeichnis nicht erstellt werden kann (z.B. read-only filesystem),
        # verwende basedir als Fallback
        try:
            os.makedirs(basedir, exist_ok=True)
            upload_base = basedir
        except (OSError, PermissionError):
            pass  # Ignoriere Fehler, wenn auch das nicht funktioniert
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

