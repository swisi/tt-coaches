"""
Flask-Anwendung Initialisierung
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

# Erstelle Flask-Instanzen
db = SQLAlchemy()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    """Lädt Benutzer für Flask-Login"""
    from app.models import User
    # Lade Benutzer direkt (Rolle wird nicht mehr benötigt, da Flags verwendet werden)
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    """App-Factory-Pattern"""
    # Bestimme das Basis-Verzeichnis (ein Verzeichnis über 'app')
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_dir = os.path.join(basedir, 'templates')
    static_dir = os.path.join(basedir, 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config_class)
    
    # Initialisiere Erweiterungen
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Bitte melden Sie sich an, um auf diese Seite zuzugreifen.'
    login_manager.login_message_category = 'info'
    
    # Initialisiere Upload-Verzeichnisse
    config_class.init_app(app)
    
    # Registriere Blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from app.coach import bp as coach_bp
    app.register_blueprint(coach_bp, url_prefix='/coach')
    
    return app

