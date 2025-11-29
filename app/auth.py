from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.zitadel import get_zitadel_authorize_url, handle_zitadel_callback, get_zitadel_logout_url, get_zitadel_password_change_url

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Leitet zur Zitadel OAuth2 Authorization weiter"""
    # Prüfe ob Benutzer bereits eingeloggt ist
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    
    # Speichere next_page in der Session für nach dem Callback
    next_page = request.args.get('next')
    if next_page and next_page.startswith('/'):
        session['next_page'] = next_page
    
    # Weiterleitung zu Zitadel Login
    return get_zitadel_authorize_url(prompt='login')

@bp.route('/callback')
def callback():
    """Verarbeitet den OAuth2 Callback von Zitadel"""
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    
    user, error = handle_zitadel_callback()
    
    if error or not user:
        flash(f'Fehler bei der Anmeldung: {error or "Unbekannter Fehler"}', 'error')
        return redirect(url_for('auth.login'))
    
    # Benutzer einloggen (remember=False, damit Session nicht permanent ist)
    login_user(user, remember=False)
    
    # Weiterleitung - IMMER zu Dashboard, nicht zu Profile
    # Die before_request Funktion wird dann automatisch zu Profile weiterleiten falls nötig
    next_page = session.pop('next_page', None)
    if not next_page or not next_page.startswith('/'):
        next_page = url_for('routes.dashboard')
    
    flash('Erfolgreich angemeldet!', 'success')
    return redirect(next_page)

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Leitet zur Zitadel Registrierungsseite weiter"""
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    
    # Weiterleitung zu Zitadel Registrierung
    return get_zitadel_authorize_url(prompt='register')

@bp.route('/logout')
@login_required
def logout():
    """Meldet den Benutzer ab und leitet zu Zitadel Logout weiter"""
    from flask import make_response, g
    import urllib.parse
    
    # Speichere Zitadel User ID für Logout-URL
    zitadel_user_id = current_user.zitadel_user_id
    
    # WICHTIG: Flask-Login Logout ZUERST aufrufen (löscht die Session)
    logout_user()
    
    # Session komplett löschen - alle Keys entfernen
    session.clear()
    
    # Stelle sicher, dass Flask-Login den Benutzer nicht mehr cached
    if hasattr(g, 'user'):
        delattr(g, 'user')
    
    # Weiterleitung zu Zitadel Logout mit Post-Logout Redirect
    logout_url = get_zitadel_logout_url()
    post_logout_redirect_uri = url_for('auth.login', _external=True)
    
    # Zitadel Logout-URL mit Parametern
    # Hinweis: id_token_hint wird weggelassen, da es optional ist und ein ID-Token erfordert
    params = {
        'post_logout_redirect_uri': post_logout_redirect_uri
    }
    
    logout_url_with_params = f"{logout_url}?{urllib.parse.urlencode(params)}"
    
    # Erstelle Response mit Cookie-Löschung
    response = make_response(redirect(logout_url_with_params))
    
    # Session-Cookie explizit löschen
    session_cookie_name = current_app.config.get('SESSION_COOKIE_NAME', 'session')
    response.set_cookie(
        session_cookie_name, 
        '', 
        expires=0, 
        max_age=0,
        path='/',
        domain=None,
        secure=False,
        httponly=True,
        samesite='Lax'
    )
    
    # Flask-Login "Remember Me" Cookie löschen (falls vorhanden)
    remember_cookie_name = current_app.config.get('REMEMBER_COOKIE_NAME', 'remember_token')
    response.set_cookie(
        remember_cookie_name,
        '',
        expires=0,
        max_age=0,
        path='/',
        domain=None,
        secure=False,
        httponly=True,
        samesite='Lax'
    )
    
    return response

@bp.route('/password/change')
@login_required
def password_change():
    """Leitet zur Zitadel Passwort-Änderungsseite weiter"""
    return redirect(get_zitadel_password_change_url())

