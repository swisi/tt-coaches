from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.forms import SignUpForm
from app.zitadel import get_zitadel_authorize_url, handle_zitadel_callback, create_zitadel_user

bp = Blueprint('auth', __name__)

@bp.route('/login')
def login():
    """Leitet zur Zitadel OAuth2 Authorization weiter"""
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    
    # Speichere next_page in der Session für nach dem Callback
    next_page = request.args.get('next')
    if next_page and next_page.startswith('/'):
        session['next_page'] = next_page
    
    # Weiterleitung zu Zitadel
    return get_zitadel_authorize_url()

@bp.route('/callback')
def callback():
    """Verarbeitet den OAuth2 Callback von Zitadel"""
    from flask import current_app
    
    if current_user.is_authenticated:
        current_app.logger.warning("auth.callback: User already authenticated, redirecting to dashboard")
        return redirect(url_for('routes.dashboard'))
    
    user, error = handle_zitadel_callback()
    
    if error or not user:
        current_app.logger.error(f"auth.callback: Error={error}")
        flash(f'Fehler bei der Anmeldung: {error or "Unbekannter Fehler"}', 'error')
        return redirect(url_for('auth.login'))
    
    # Benutzer einloggen
    login_user(user, remember=True)
    current_app.logger.info(f"auth.callback: User {user.email} logged in, profile_complete={user.is_profile_complete()}")
    
    # Weiterleitung - IMMER zu Dashboard, nicht zu Profile
    # Die before_request Funktion wird dann automatisch zu Profile weiterleiten falls nötig
    next_page = session.pop('next_page', None)
    if not next_page or not next_page.startswith('/'):
        next_page = url_for('routes.dashboard')
    
    current_app.logger.info(f"auth.callback: Redirecting to {next_page}")
    flash('Erfolgreich angemeldet!', 'success')
    return redirect(next_page)

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Registriert einen neuen Benutzer in Zitadel"""
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    
    # Prüfe ob Zitadel Management API konfiguriert ist
    from flask import current_app
    if not current_app.config.get('ZITADEL_MANAGEMENT_API_URL') or not current_app.config.get('ZITADEL_MANAGEMENT_API_TOKEN'):
        flash('Registrierung ist derzeit nicht verfügbar. Bitte kontaktiere den Administrator.', 'error')
        return redirect(url_for('auth.login'))
    
    form = SignUpForm()
    if form.validate_on_submit():
        # Prüfe ob E-Mail bereits existiert
        if User.query.filter_by(email=form.email.data).first():
            flash('Diese E-Mail-Adresse ist bereits registriert.', 'error')
            return render_template('auth/signup.html', form=form)
        
        # Erstelle Benutzer in Zitadel
        success, zitadel_user_id, error_msg = create_zitadel_user(
            form.email.data,
            form.password.data
        )
        
        if not success:
            flash(f'Fehler bei der Registrierung: {error_msg}', 'error')
            return render_template('auth/signup.html', form=form)
        
        # Erstelle lokalen Benutzer-Eintrag
        user = User(
            email=form.email.data,
            zitadel_user_id=zitadel_user_id,
            password_hash=None,  # Passwort wird von Zitadel verwaltet
            is_admin=False
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registrierung erfolgreich! Bitte melde dich jetzt an.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/signup.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Meldet den Benutzer ab"""
    logout_user()
    flash('Du wurdest erfolgreich abgemeldet.', 'info')
    
    # Optional: Weiterleitung zu Zitadel Logout
    # issuer = current_app.config['ZITADEL_ISSUER']
    # return redirect(f"{issuer}/oidc/v1/end_session")
    
    return redirect(url_for('auth.login'))

