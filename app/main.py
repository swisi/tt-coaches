"""
Haupt-Blueprint (Dashboard, Startseite)
"""
from flask import Blueprint, render_template, redirect, url_for, send_from_directory, current_app
from flask_login import login_required, current_user
from config import Config
from pathlib import Path
import os

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Startseite"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard je nach Rolle"""
    if current_user.is_superadmin() or current_user.is_admin():
        return redirect(url_for('admin.overview'))
    elif current_user.is_coach():
        return redirect(url_for('coach.overview'))
    return render_template('main/dashboard.html')

@bp.route('/favicon.ico')
def favicon():
    """Favicon-Route als Fallback"""
    # Verwende den statischen Ordner der App oder das Basis-Verzeichnis
    static_dir = current_app.static_folder if current_app else os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    return send_from_directory(static_dir, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

