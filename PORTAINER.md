# Portainer Stack Konfiguration

Anleitung zur Bereitstellung der CoachManager-Anwendung in Portainer.

## 📋 Stack-Konfiguration

Verwende diese `docker-compose.yml` Konfiguration in Portainer:

```yaml
version: '3.8'

services:
  web:
    image: ${DOCKER_HUB_USERNAME:-swisi}/coaches:${IMAGE_TAG:-latest}
    container_name: coaches-app
    ports:
      - "3000:3000"
    environment:
      - FLASK_APP=run.py
      - SECRET_KEY=${SECRET_KEY:-change-me-in-production}
      - DATABASE_PATH=/app/data
      - DATABASE_URL=sqlite:////app/data/coaches.db
      - UPLOAD_BASE=/app
    pull_policy: always
    volumes:
      # Datenbank-Persistenz
      - coaches-data:/app/data
      # Upload-Dateien
      - coaches-uploads:/app/app/static/uploads
      # Instance-Config
      - coaches-instance:/app/instance
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:3000/auth/login')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  coaches-data:
  coaches-uploads:
  coaches-instance:
```

## ⚠️ Wichtige Hinweise

### DATABASE_URL Format

**WICHTIG:** SQLite benötigt **4 Slashes** für absolute Pfade:
- ✅ **Korrekt:** `sqlite:////app/data/coaches.db` (4 Slashes)
- ❌ **Falsch:** `sqlite:///data/coaches.db` (3 Slashes - relativer Pfad)

### Umgebungsvariablen

Du kannst folgende Umgebungsvariablen in Portainer setzen:

| Variable | Beschreibung | Standard |
|----------|-------------|----------|
| `DOCKER_HUB_USERNAME` | Docker Hub Username | `swisi` |
| `IMAGE_TAG` | Image Version | `latest` |
| `SECRET_KEY` | Flask Secret Key | `change-me-in-production` |

### Volumes

Die Anwendung verwendet Docker Volumes für Datenpersistenz:
- `coaches-data`: Datenbank-Dateien
- `coaches-uploads`: Hochgeladene Zertifikate
- `coaches-instance`: Flask-Instance-Konfiguration

## 🚀 Setup in Portainer

1. **Gehe zu Stacks** → **Add stack**
2. **Füge die obige docker-compose.yml ein**
3. **Setze Umgebungsvariablen** (optional):
   - `DOCKER_HUB_USERNAME`: Dein Docker Hub Username
   - `IMAGE_TAG`: Version (z.B. `1.0.0` oder `latest`)
   - `SECRET_KEY`: Ein sicheres Secret Key
4. **Deploy the stack**
5. **Öffne die Anwendung** unter `http://dein-server:3000`

## 🔧 Troubleshooting

### Fehler: "unable to open database file"

**Ursache:** Falsche `DATABASE_URL` Format.

**Lösung:** Stelle sicher, dass `DATABASE_URL` **4 Slashes** hat:
```yaml
DATABASE_URL=sqlite:////app/data/coaches.db
```

### Fehler: "Permission denied"

**Ursache:** Volume-Berechtigungen.

**Lösung:** Die Anwendung erstellt automatisch die benötigten Verzeichnisse beim Start.

### Container startet nicht

**Prüfe:**
1. Logs: `docker logs coaches-app`
2. Healthcheck: `docker inspect coaches-app`
3. Umgebungsvariablen in Portainer

## 📝 Erster Admin-Benutzer

Beim ersten Start wird automatisch ein Admin-Benutzer erstellt:
- **E-Mail:** `admin@schweizer.be`
- **Passwort:** `admin123`

**WICHTIG:** Ändere das Passwort nach dem ersten Login!

## 🔄 Updates

Um auf eine neue Version zu aktualisieren:

1. **Setze `IMAGE_TAG`** auf die gewünschte Version (z.B. `1.0.0`)
2. **Redeploy** den Stack in Portainer
3. Das Image wird automatisch von Docker Hub geladen

