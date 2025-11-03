"""
Hauptdatei zum Starten der Flask-Anwendung
"""
from app import create_app, db
from app.models import User, Role, TrainerProfile, Certificate

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Shell-Kontext für Flask Shell"""
    return {'db': db, 'User': User, 'Role': Role, 'TrainerProfile': TrainerProfile, 'Certificate': Certificate}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

