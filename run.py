from app import create_app, db
from app.models import User

app = create_app()

# Für Gunicorn
application = app

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

def init_db():
    """Initialisiert die Datenbank und erstellt Admin-Benutzer"""
    with app.app_context():
        import os
        # Stelle sicher, dass das Datenbank-Verzeichnis existiert
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            # Extrahiere den Pfad aus der SQLite URI
            db_path = db_uri.replace('sqlite:///', '').replace('sqlite:////', '')
            db_dir = os.path.dirname(db_path)
            if db_dir:
                try:
                    os.makedirs(db_dir, exist_ok=True)
                except (OSError, PermissionError) as e:
                    # Falls Docker-Pfad lokal nicht funktioniert, verwende lokalen Fallback
                    if '/app/' in db_path:
                        print(f"Warnung: Docker-Pfad {db_dir} nicht verfügbar, verwende lokalen Fallback")
                        # Verwende lokalen Pfad als Fallback
                        local_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "coaches.db")
                        local_db_uri = f'sqlite:///{local_db_path}'
                        app.config['SQLALCHEMY_DATABASE_URI'] = local_db_uri
                        db_uri = local_db_uri
                        db_path = local_db_path
                        db_dir = os.path.dirname(db_path)
                        os.makedirs(db_dir, exist_ok=True)
                    else:
                        print(f"FEHLER: Kann Datenbank-Verzeichnis nicht erstellen: {db_dir}")
                        print(f"Fehlerdetails: {e}")
                        raise
        
        # Migrationen ausführen
        from flask_migrate import upgrade
        try:
            upgrade()
            print("Datenbank-Migrationen erfolgreich ausgeführt.")
        except Exception as e:
            print(f"Warnung bei Migrationen: {e}")
            # Fallback: db.create_all() falls Migrationen fehlschlagen
            try:
                db.create_all()
                print("Datenbank mit db.create_all() erstellt.")
            except Exception as e2:
                print(f"FEHLER: Kann Datenbank nicht erstellen: {e2}")
                raise
        
        # Ersten Admin erstellen falls keiner existiert
        if not User.query.filter_by(is_admin=True).first():
            admin = User(
                email='admin@schweizer.be',
                first_name='Admin',
                last_name='User',
                full_name='Admin User',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("=" * 50)
            print("Admin-Benutzer erstellt!")
            print("E-Mail: admin@schweizer.be")
            print("Passwort: admin123")
            print("=" * 50)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=3000)
else:
    # Für Gunicorn: Datenbank initialisieren
    init_db()

