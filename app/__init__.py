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
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Datenbank-Verzeichnis erstellen (falls nicht vorhanden)
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///'):
        # Extrahiere den Pfad aus der SQLite URI
        db_path = db_uri.replace('sqlite:///', '')
        # Entferne den Dateinamen, um nur das Verzeichnis zu bekommen
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
    
    return app

