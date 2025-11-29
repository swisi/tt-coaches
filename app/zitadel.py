"""
Zitadel Integration Modul
Handles OAuth2/OIDC authentication and user management via Zitadel API
"""
import requests
from flask import current_app, url_for, session, redirect
from authlib.integrations.flask_client import OAuth
from app import db
from app.models import User

oauth = OAuth()

def init_zitadel_oauth(app):
    """Initialisiert Zitadel OAuth2 Client"""
    oauth.init_app(app)
    
    oauth.register(
        name='zitadel',
        client_id=app.config['ZITADEL_CLIENT_ID'],
        client_secret=app.config['ZITADEL_CLIENT_SECRET'],
        server_metadata_url=f"{app.config['ZITADEL_ISSUER']}/.well-known/openid-configuration",
        client_kwargs={
            'scope': 'openid email profile',
            'response_type': 'code'
        }
    )

def get_zitadel_authorize_url():
    """Gibt die Zitadel Authorization URL zurück"""
    redirect_uri = url_for('auth.callback', _external=True)
    current_app.logger.debug(f"Zitadel redirect_uri: {redirect_uri}")
    return oauth.zitadel.authorize_redirect(redirect_uri)

def handle_zitadel_callback():
    """Verarbeitet den OAuth2 Callback von Zitadel"""
    try:
        token = oauth.zitadel.authorize_access_token()
        current_app.logger.debug(f"Zitadel token received: {list(token.keys())}")
        
        # Hole Userinfo separat über den Userinfo-Endpoint
        access_token = token.get('access_token')
        if not access_token:
            current_app.logger.error("No access_token in token response")
            return None, "Kein Access Token erhalten"
        
        # Hole Userinfo von Zitadel
        metadata_url = f"{current_app.config['ZITADEL_ISSUER']}/.well-known/openid-configuration"
        try:
            metadata_response = requests.get(metadata_url, timeout=10)
            metadata_response.raise_for_status()
            metadata = metadata_response.json()
        except Exception as e:
            current_app.logger.error(f"Error fetching metadata: {str(e)}")
            return None, f"Fehler beim Abrufen der Zitadel-Konfiguration: {str(e)}"
        
        userinfo_endpoint = metadata.get('userinfo_endpoint')
        if not userinfo_endpoint:
            current_app.logger.error("No userinfo_endpoint in metadata")
            return None, "Userinfo-Endpoint nicht gefunden"
        
        # Rufe Userinfo ab
        headers = {'Authorization': f'Bearer {access_token}'}
        try:
            user_info_response = requests.get(userinfo_endpoint, headers=headers, timeout=10)
            user_info_response.raise_for_status()
            user_info = user_info_response.json()
            current_app.logger.debug(f"Userinfo received: {list(user_info.keys())}")
        except Exception as e:
            current_app.logger.error(f"Error fetching userinfo: {str(e)}, Response: {user_info_response.text if 'user_info_response' in locals() else 'N/A'}")
            return None, f"Fehler beim Abrufen der Benutzerinformationen: {str(e)}"
        
        if not user_info:
            current_app.logger.error("Empty user_info response")
            return None, "Keine Benutzerinformationen erhalten"
        
        # Extrahiere Benutzerinformationen
        zitadel_user_id = user_info.get('sub')
        email = user_info.get('email') or user_info.get('preferred_username') or user_info.get('username')
        name = user_info.get('name', '') or user_info.get('given_name', '')
        
        current_app.logger.debug(f"Extracted: user_id={zitadel_user_id}, email={email}, name={name}")
        
        if not zitadel_user_id:
            current_app.logger.error(f"Missing 'sub' in user_info: {user_info}")
            return None, "Keine User ID in Benutzerinformationen gefunden"
        
        if not email:
            current_app.logger.error(f"Missing email in user_info: {user_info}")
            return None, "Keine E-Mail-Adresse in Benutzerinformationen gefunden"
        
        # Suche oder erstelle Benutzer in der lokalen Datenbank
        user = User.query.filter_by(zitadel_user_id=zitadel_user_id).first()
        
        if not user:
            # Prüfe ob Benutzer mit dieser E-Mail bereits existiert (Migration)
            user = User.query.filter_by(email=email).first()
            if user:
                # Migriere bestehenden Benutzer zu Zitadel
                user.zitadel_user_id = zitadel_user_id
                user.password_hash = None  # Passwort wird nicht mehr lokal gespeichert
            else:
                # Erstelle neuen Benutzer
                user = User(
                    email=email,
                    zitadel_user_id=zitadel_user_id,
                    password_hash=None,
                    is_admin=False
                )
                db.session.add(user)
        
        # Aktualisiere E-Mail falls sich geändert hat
        if user.email != email:
            user.email = email
        
        # Aktualisiere Name falls vorhanden
        if name and not user.full_name:
            user.full_name = name
        
        db.session.commit()
        
        return user, None
        
    except Exception as e:
        current_app.logger.error(f"Fehler bei Zitadel Callback: {str(e)}")
        return None, f"Fehler bei der Authentifizierung: {str(e)}"

def create_zitadel_user(email, password):
    """
    Erstellt einen neuen Benutzer in Zitadel über die Management API
    Gibt (success, user_id, error_message) zurück
    
    Hinweis: Die genaue API-Struktur hängt von der Zitadel-Version ab.
    Diese Implementierung verwendet die Standard-Zitadel Management API v2.
    """
    try:
        api_url = current_app.config['ZITADEL_MANAGEMENT_API_URL']
        api_token = current_app.config['ZITADEL_MANAGEMENT_API_TOKEN']
        default_role = current_app.config['ZITADEL_DEFAULT_ROLE']
        
        if not api_url or not api_token:
            return False, None, "Zitadel Management API nicht konfiguriert. Bitte setze ZITADEL_MANAGEMENT_API_URL und ZITADEL_MANAGEMENT_API_TOKEN in der Konfiguration."
        
        # Erstelle Benutzer in Zitadel
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        # Zitadel Management API v2 Endpoint für Human User Creation
        # Format: {api_url}/management/v1/users/human/_import
        # Oder: {api_url}/management/v1/users/human (für normale Erstellung)
        create_user_url = f"{api_url.rstrip('/')}/management/v1/users/human/_import"
        
        user_data = {
            'userName': email,
            'email': {
                'email': email,
                'isEmailVerified': False  # Benutzer muss E-Mail verifizieren
            },
            'password': {
                'password': password,
                'changeRequired': False
            }
        }
        
        response = requests.post(create_user_url, json=user_data, headers=headers)
        
        if response.status_code not in [200, 201]:
            try:
                error_data = response.json()
                error_msg = error_data.get('message') or error_data.get('details') or str(error_data)
            except:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
            current_app.logger.error(f"Zitadel API Fehler: {error_msg}")
            return False, None, f"Fehler beim Erstellen des Benutzers in Zitadel: {error_msg}"
        
        try:
            user_data_response = response.json()
            zitadel_user_id = user_data_response.get('userId') or user_data_response.get('id')
        except:
            # Falls die Antwort kein JSON ist, versuche die User ID aus dem Header zu extrahieren
            location = response.headers.get('Location', '')
            if location:
                zitadel_user_id = location.split('/')[-1]
            else:
                zitadel_user_id = None
        
        if not zitadel_user_id:
            current_app.logger.warning(f"Keine User ID in Zitadel-Antwort erhalten. Response: {response.text[:200]}")
            # Versuche alternativ die User ID über die User-Info zu erhalten
            # Dies ist ein Workaround falls die API-Struktur anders ist
            return False, None, "Keine User ID von Zitadel erhalten. Bitte prüfe die Zitadel-Konfiguration."
        
        # Weise Standard-Rolle zu (falls konfiguriert)
        # Hinweis: Rollenzuweisung erfordert normalerweise eine Project/Application ID
        # Dies sollte in der Zitadel-Konfiguration gesetzt werden
        if default_role:
            try:
                # Rollenzuweisung erfolgt normalerweise über Project Memberships
                # Die genaue Implementierung hängt von der Zitadel-Konfiguration ab
                current_app.logger.info(f"Standard-Rolle '{default_role}' sollte in Zitadel konfiguriert werden")
            except Exception as e:
                current_app.logger.warning(f"Konnte Rolle nicht zuweisen: {str(e)}")
        
        return True, zitadel_user_id, None
        
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Netzwerk-Fehler beim Erstellen des Zitadel-Benutzers: {str(e)}")
        return False, None, f"Netzwerk-Fehler: {str(e)}"
    except Exception as e:
        current_app.logger.error(f"Fehler beim Erstellen des Zitadel-Benutzers: {str(e)}")
        return False, None, f"Fehler beim Erstellen des Benutzers: {str(e)}"

def get_zitadel_password_change_url():
    """Gibt die URL für Passwort-Änderung in Zitadel zurück"""
    issuer = current_app.config['ZITADEL_ISSUER']
    # Zitadel hat normalerweise eine Passwort-Änderungsseite
    # Die genaue URL hängt von der Zitadel-Konfiguration ab
    return f"{issuer}/ui/login/password/change"

