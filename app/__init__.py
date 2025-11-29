from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Bitte melde dich an, um auf diese Seite zuzugreifen.'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # User loader für Flask-Login
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except (ValueError, TypeError):
            return None
    
    # Zitadel OAuth initialisieren
    from app.zitadel import init_zitadel_oauth
    init_zitadel_oauth(app)
    
    # Blueprints registrieren
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    # Upload-Ordner erstellen
    import os
    upload_folder = app.config.get('UPLOAD_FOLDER', 'app/static/uploads/certificates')
    try:
        os.makedirs(upload_folder, exist_ok=True)
        app.logger.debug(f"Upload-Ordner erstellt/geprüft: {upload_folder}")
    except (OSError, PermissionError) as e:
        # Falls das Verzeichnis nicht erstellt werden kann
        app.logger.warning(f"Konnte Upload-Ordner nicht erstellen: {upload_folder}, Fehler: {e}")
        # Nur Fallback für lokale Entwicklung (nicht für Docker)
        if not upload_folder.startswith('/app'):
            # Lokale Entwicklung: Versuche Fallback
            local_upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'app', 'static', 'uploads', 'certificates')
            try:
                os.makedirs(local_upload_folder, exist_ok=True)
                app.config['UPLOAD_FOLDER'] = local_upload_folder
                app.logger.info(f"Verwende Fallback Upload-Ordner: {local_upload_folder}")
            except (OSError, PermissionError):
                app.logger.error(f"Konnte auch Fallback Upload-Ordner nicht erstellen: {local_upload_folder}")
                pass  # Ignoriere Fehler, wenn auch das nicht funktioniert
        else:
            # Docker: Logge Warnung, aber ändere nicht den Pfad
            app.logger.warning(f"Docker: Upload-Ordner {upload_folder} konnte nicht erstellt werden. Stelle sicher, dass das Volume korrekt gemountet ist.")
    
    # Datenbank-Verzeichnis erstellen (falls nicht vorhanden)
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///'):
        # Extrahiere den Pfad aus der SQLite URI
        db_path = db_uri.replace('sqlite:///', '')
        # Entferne den Dateinamen, um nur das Verzeichnis zu bekommen
        db_dir = os.path.dirname(db_path)
        if db_dir:
            try:
                os.makedirs(db_dir, exist_ok=True)
            except (OSError, PermissionError):
                pass  # Ignoriere Fehler, wenn das Verzeichnis nicht erstellt werden kann
    
    return app

