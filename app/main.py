"""
Haupt-Blueprint (Dashboard, Startseite)
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

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

