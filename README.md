# TT-Coaches Verwaltungssystem

Eine Flask-basierte Webanwendung zur Verwaltung von Trainerdaten, Zertifikaten und Benutzern mit rollenbasierter Zugriffskontrolle.

## Funktionen

### Benutzer- und Rollenmodell

- **Super-Administrator**: Vollständige Rechte für Verwaltung und Zugriff
- **Administrator** (Mitglied der Ausbildungskommission): Kann Trainerdaten und Benutzer verwalten, keine Superadmins erstellen/löschen
- **Coach** (Trainer): Kann nur eigene Daten erfassen und bearbeiten

### Funktionen für Trainer/Coaches

- Eingabe und Pflege persönlicher Daten (Name, Adresse, Telefonnummern, E-Mail-Adressen, Funktion im Club)
- Erfassung des Curriculum vitae als Trainer (strukturierte Felder und/oder Datei-Upload)
- Hinzufügen weiterer Zertifikate mit Upload von Bild- oder PDF-Bestätigungen

### Administratoren und Superadmin

- Übersicht und Verwaltung aller Benutzer und Trainerdaten
- Einsehen und Bearbeiten von Lebensläufen und Zertifikaten
- Löschmöglichkeit für Einträge (restriktiv für Superadmins)

## Voraussetzungen

- Python 3.8 oder höher
- MariaDB/MySQL Datenbankserver
- pip (Python Package Manager)

## Installation

### 1. Repository klonen oder Dateien entpacken

```bash
cd tt-coaches
```

### 2. Virtuelle Umgebung erstellen (empfohlen)

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 3. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### 4. Datenbank konfigurieren

Bearbeiten Sie die Datei `config.py` und passen Sie die Datenbankverbindung an:

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://benutzername:passwort@localhost/datenbankname?charset=utf8mb4'
```

Erstellen Sie eine leere Datenbank in MariaDB:

```sql
CREATE DATABASE tt_coaches CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Datenbank initialisieren

```bash
python init_db.py
```

Dies erstellt:
- Alle notwendigen Tabellen
- Die drei Rollen (superadmin, admin, coach)
- Einen initialen Superadministrator (Benutzername: `admin`, Passwort: `admin123`)

**WICHTIG**: Ändern Sie das Passwort nach dem ersten Login!

### 6. Anwendung starten

```bash
python run.py
```

Die Anwendung läuft dann unter `http://localhost:5000`

## Projektstruktur

```
tt-coaches/
├── app/
│   ├── __init__.py          # Flask-App Initialisierung
│   ├── models.py            # Datenbank-Modelle
│   ├── auth.py              # Authentifizierungs-Routen
│   ├── main.py              # Haupt-Routen (Dashboard)
│   ├── admin.py             # Admin-Routen
│   ├── coach.py             # Coach-Routen
│   ├── forms.py             # WTForms-Formulare
│   └── utils.py             # Hilfsfunktionen
├── templates/
│   ├── base.html            # Basis-Template
│   ├── auth/
│   │   └── login.html
│   ├── coach/
│   │   ├── profile.html
│   │   ├── certificates.html
│   │   └── add_certificate.html
│   └── admin/
│       ├── overview.html
│       ├── users.html
│       ├── user_detail.html
│       ├── trainers.html
│       ├── trainer_detail.html
│       └── edit_trainer.html
├── uploads/                 # Hochgeladene Dateien
│   ├── certificates/
│   └── cv/
├── config.py                # Konfiguration
├── run.py                   # Hauptdatei zum Starten
├── init_db.py               # Datenbank-Initialisierung
├── requirements.txt         # Python-Abhängigkeiten
└── README.md               # Diese Datei
```

## Verwendung

### Erster Login

1. Öffnen Sie `http://localhost:5000` im Browser
2. Melden Sie sich mit den Standard-Credentials an:
   - Benutzername: `admin`
   - Passwort: `admin123`
3. **Ändern Sie sofort das Passwort** (über Admin-Funktionen)

### Neue Benutzer erstellen

**Über das Admin-Interface:**
Als Superadministrator oder Administrator können Sie neue Benutzer in der Benutzerverwaltung erstellen.

**Über die Kommandozeile:**
Sie können auch das Hilfsskript `create_user.py` verwenden:

```bash
python create_user.py --username trainer1 --email trainer1@example.com --role coach --password pass123
```

Verfügbare Rollen: `superadmin`, `admin`, `coach`

### Produktionsumgebung

Für den Einsatz in einer Produktionsumgebung:

1. Ändern Sie `SECRET_KEY` in `config.py` (oder setzen Sie die Umgebungsvariable)
2. Verwenden Sie einen Produktions-WSGI-Server (z.B. Gunicorn, uWSGI)
3. Konfigurieren Sie einen Reverse Proxy (z.B. Nginx)
4. Aktivieren Sie HTTPS
5. Konfigurieren Sie regelmäßige Backups der Datenbank
6. Überprüfen Sie die Dateiberechtigungen für das `uploads/` Verzeichnis

## Erweiterungen

Die Codebasis ist modular aufgebaut und kann einfach erweitert werden:

- Weitere Rollen können in `models.py` hinzugefügt werden
- Neue Funktionen können als zusätzliche Blueprints implementiert werden
- Das Datenbankschema kann durch Migrationen (z.B. Flask-Migrate) erweitert werden
- Weitere Formularfelder können in `forms.py` ergänzt werden

## Technologie-Stack

- **Backend**: Flask 3.0
- **Datenbank**: MariaDB/MySQL mit SQLAlchemy ORM
- **Authentifizierung**: Flask-Login
- **Formulare**: Flask-WTF / WTForms
- **Frontend**: Bootstrap 5.3 (responsive Design)
- **Template-Engine**: Jinja2

## Lizenz

Siehe LICENSE-Datei

## Support

Bei Fragen oder Problemen wenden Sie sich bitte an den Projektverantwortlichen.

