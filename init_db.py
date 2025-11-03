"""
Initialisierungsskript für die Datenbank
Erstellt das Datenbankschema und initiale Rollen
"""
from app import create_app, db
from app.models import User, Role

def init_db():
    """Initialisiert die Datenbank"""
    app = create_app()
    
    with app.app_context():
        # Erstelle alle Tabellen
        db.create_all()
        print("✓ Datenbanktabellen erstellt")
        
        # Erstelle Rollen falls sie noch nicht existieren
        roles = [
            {'name': 'superadmin', 'description': 'Superadministrator mit vollständigen Rechten'},
            {'name': 'admin', 'description': 'Administrator (Mitglied der Ausbildungskommission)'},
            {'name': 'coach', 'description': 'Trainer/Coach'}
        ]
        
        for role_data in roles:
            role = Role.query.filter_by(name=role_data['name']).first()
            if not role:
                role = Role(**role_data)
                db.session.add(role)
                print(f"✓ Rolle '{role_data['name']}' erstellt")
        
        db.session.commit()
        
        # Erstelle einen initialen Superadministrator falls noch kein Superadmin existiert
        superadmin_role = Role.query.filter_by(name='superadmin').first()
        if superadmin_role:
            existing_superadmin = User.query.filter_by(role_id=superadmin_role.id).first()
            if not existing_superadmin:
                superadmin = User(
                    username='admin',
                    email='admin@example.com',
                    role_id=superadmin_role.id,
                    active=True
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

