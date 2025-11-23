from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.forms import LoginForm, SignUpForm

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                # Prüfe Profilvollständigkeit
                if not user.is_profile_complete():
                    next_page = url_for('routes.profile')
                else:
                    next_page = url_for('routes.dashboard')
            return redirect(next_page)
        else:
            flash('Ungültige E-Mail oder Passwort.', 'error')
    
    return render_template('auth/login.html', form=form)

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    
    form = SignUpForm()
    if form.validate_on_submit():
        # Prüfe ob E-Mail bereits existiert
        if User.query.filter_by(email=form.email.data).first():
            flash('Diese E-Mail-Adresse ist bereits registriert.', 'error')
            return render_template('auth/signup.html', form=form)
        
        # Neuen Benutzer erstellen
        user = User(
            email=form.email.data,
            is_admin=False  # Standard ist kein Admin
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registrierung erfolgreich! Bitte melde dich an.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/signup.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Du wurdest erfolgreich abgemeldet.', 'info')
    return redirect(url_for('auth.login'))

