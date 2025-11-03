"""
Hilfsskript zum Erstellen neuer Benutzer
Beispiel-Verwendung:
    python create_user.py --username trainer1 --email trainer1@example.com --role coach --password pass123
"""
import argparse
from app import create_app, db
from app.models import User, Role

def create_user(username, email, password, role_name):
    """Erstellt einen neuen Benutzer"""
    app = create_app()
    
    with app.app_context():
        # Prüfe ob Benutzer bereits existiert
        if User.query.filter_by(username=username).first():
            print(f"Fehler: Benutzer '{username}' existiert bereits.")
            return False
        
        if User.query.filter_by(email=email).first():
            print(f"Fehler: E-Mail '{email}' wird bereits verwendet.")
            return False
        
        # Hole Rolle
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            print(f"Fehler: Rolle '{role_name}' existiert nicht.")
            print("Verfügbare Rollen: superadmin, admin, coach")
            return False
        
        # Erstelle Benutzer
        user = User(
            username=username,
            email=email,
            role_id=role.id,
            active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        print(f"✓ Benutzer '{username}' erfolgreich erstellt")
        print(f"  E-Mail: {email}")
        print(f"  Rolle: {role_name}")
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Erstellt einen neuen Benutzer')
    parser.add_argument('--username', required=True, help='Benutzername')
    parser.add_argument('--email', required=True, help='E-Mail-Adresse')
    parser.add_argument('--password', required=True, help='Passwort')
    parser.add_argument('--role', required=True, choices=['superadmin', 'admin', 'coach'], help='Rolle')
    
    args = parser.parse_args()
    
    create_user(args.username, args.email, args.password, args.role)

