"""
Initialisierungsskript für die Datenbank
Erstellt das Datenbankschema und initialen Superadministrator
"""
from app import create_app, db
from app.models import User

def init_db():
    """Initialisiert die Datenbank"""
    app = create_app()
    
    with app.app_context():
        # Erstelle alle Tabellen
        db.create_all()
        print("✓ Datenbanktabellen erstellt")
        
        # Erstelle einen initialen Superadministrator falls noch kein Superadmin existiert
        existing_superadmin = User.query.filter_by(is_superadmin=True).first()
        if not existing_superadmin:
            superadmin = User(
                username='admin',
                email='admin@example.com',
                active=True,
                is_superadmin=True,
                is_admin=False,
                is_coach=False
            )
            superadmin.set_password('admin123')  # BITTE IN PRODUKTION ÄNDERN!
            db.session.add(superadmin)
            db.session.commit()
            print("✓ Initialer Superadministrator erstellt")
            print("  Benutzername: admin")
            print("  Passwort: admin123")
            print("  WICHTIG: Bitte ändern Sie das Passwort nach dem ersten Login!")
        
        print("\n✓ Datenbankinitialisierung abgeschlossen")

if __name__ == '__main__':
    init_db()

