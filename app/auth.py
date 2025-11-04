"""
Authentifizierungs-Blueprint
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, TrainerProfile
from app.forms import LoginForm, RegisterForm

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login-Seite"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            if user.active:
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('main.dashboard')
                return redirect(next_page)
            else:
                flash('Ihr Konto ist deaktiviert.', 'error')
        else:
            flash('Ungültiger Benutzername oder Passwort.', 'error')
    
    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registrierungsseite für Coaches"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Erstelle neuen Benutzer direkt mit Coach-Flag
        user = User(
            username=form.username.data,
            email=form.email.data,
            active=True,
            is_coach=True  # Direkt als Coach registrieren
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.flush()  # Um user.id zu erhalten
        
        # Erstelle leeres Trainer-Profil
        trainer_profile = TrainerProfile(
            user_id=user.id,
            first_name='',
            last_name=''
        )
        db.session.add(trainer_profile)
        db.session.commit()
        
        flash('Registrierung erfolgreich! Sie können sich jetzt anmelden.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    flash('Sie wurden erfolgreich abgemeldet.', 'info')
    return redirect(url_for('auth.login'))

