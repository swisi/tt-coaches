# CoachManager - American Football Coaching Management System

Eine umfassende Flask-Webanwendung zur Verwaltung von American Football Coaches, ihren Qualifikationen, Erfahrungen und Trainingsplänen.

## 🚀 Features

- **Dashboard**: Übersicht über Coaching-Aktivitäten und Statistiken
- **Profilverwaltung**: Vollständige Verwaltung persönlicher Coach-Daten
- **Zertifikate-Management**: Dokumentation von Coaching-Qualifikationen mit Datei-Upload
- **Erfahrungsverwaltung**: Lückenlose Dokumentation der Coaching-Laufbahn
- **Coaches-Übersicht**: Suche und Anzeige aller registrierten Coaches
- **Trainingspläne**: Detaillierte Wochenplanung mit Live-Tracking
- **Admin-Bereich**: Vollständige Verwaltung aller Coaches und Trainingspläne
- **CSV-Export**: Export aller Coach-Daten

## 📋 Voraussetzungen

- Python 3.12+
- pip (Python Package Manager)

## 🔧 Installation

1. **Virtual Environment aktivieren** (falls noch nicht aktiv):
```bash
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows
```

2. **Abhängigkeiten installieren**:
```bash
pip install -r requirements.txt
```

3. **Umgebungsvariablen einrichten** (optional):
```bash
cp .env.example .env
# Bearbeite .env und setze SECRET_KEY und DATABASE_URL
```

4. **Datenbank initialisieren**:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 🏃 Starten der Anwendung

```bash
python run.py
```

Die Anwendung läuft dann unter: `http://localhost:3000`

### Standard-Admin-Zugangsdaten

Beim ersten Start wird automatisch ein Admin-Benutzer erstellt:
- **E-Mail**: `admin@schweizer.be`
- **Passwort**: `admin123`

⚠️ **Wichtig**: Ändere das Passwort nach dem ersten Login!

## 📁 Projektstruktur

```
coaches/
├── app/
│   ├── __init__.py          # Flask-App Initialisierung
│   ├── models.py             # Datenmodelle (User, Certificate, etc.)
│   ├── forms.py              # Flask-WTF Formulare
│   ├── routes.py             # Alle Routen
│   ├── auth.py               # Authentifizierung
│   ├── utils.py              # Hilfsfunktionen
│   ├── templates/            # Jinja2 Templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── profile.html
│   │   ├── certificates.html
│   │   ├── experience.html
│   │   ├── coaches.html
│   │   ├── training_plans.html
│   │   ├── training_plan_detail.html
│   │   ├── admin/
│   │   └── auth/
│   └── static/
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── main.js
│       └── uploads/
│           └── certificates/
├── migrations/               # Flask-Migrate Datenbank-Migrationen
├── config.py                 # Konfiguration
├── requirements.txt          # Python-Abhängigkeiten
└── run.py                    # Start-Skript
```

## 🎯 Verwendung

### Für Coaches

1. **Erstanmeldung**: Login mit E-Mail und Passwort
2. **Profil vervollständigen**: Alle Pflichtfelder ausfüllen
3. **Zertifikate hinzufügen**: Coaching-Qualifikationen dokumentieren
4. **Erfahrung eintragen**: Coaching-Laufbahn dokumentieren
5. **Trainingspläne ansehen**: Aktuelle Trainingspläne des eigenen Teams

### Für Administratoren

1. **Coaches verwalten**: Übersicht aller Coaches, Bearbeitung, Passwort-Reset
2. **Trainingspläne erstellen**: Neue Pläne mit Aktivitäten anlegen
3. **CSV-Export**: Alle Coach-Daten exportieren
4. **Vollzugriff**: Auf alle Funktionen der Anwendung

## 🔒 Sicherheit

- Passwörter werden mit Werkzeug gehasht
- CSRF-Schutz durch Flask-WTF
- Session-Management durch Flask-Login
- Datei-Upload-Validierung
- Rollenbasierte Zugriffskontrolle

## 🎨 Design

- **Dark Mode**: Automatische Erkennung der System-Präferenz
- **Responsive**: Funktioniert auf Desktop, Tablet und Mobile
- **Tailwind CSS**: Moderne, konsistente UI
- **Accessible**: Barrierefreie Bedienelemente

## 📝 Datenbank-Migrationen

Bei Änderungen an den Modellen:

```bash
flask db migrate -m "Beschreibung der Änderung"
flask db upgrade
```

## 🐛 Fehlerbehebung

### Datenbank-Fehler
```bash
# Datenbank zurücksetzen (ACHTUNG: Löscht alle Daten!)
rm coaches.db
flask db upgrade
```

### Port bereits belegt
Ändere den Port in `run.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

## 📄 Lizenz

Diese Anwendung wurde speziell für den Einsatz in American Football Vereinen entwickelt.

## 🙏 Danksagungen

- Flask für das Web-Framework
- SQLAlchemy für die Datenbank-ORM
- Tailwind CSS für das Styling

---

**Version**: 1.0  
**Letztes Update**: November 2025  
**Status**: Produktionsbereit

