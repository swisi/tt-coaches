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
        # Datenbank erstellen falls nicht vorhanden
        db.create_all()
        
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

