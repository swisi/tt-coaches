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
      - MAX_CONTENT_LENGTH=${MAX_CONTENT_LENGTH:-524288000}  # 500MB default (für große Backup-Dateien)
      # Zitadel OAuth2/OIDC Konfiguration (ERFORDERLICH)
      - ZITADEL_ISSUER=${ZITADEL_ISSUER:-https://tt-auth.swisi.net}
      - ZITADEL_CLIENT_ID=${ZITADEL_CLIENT_ID}
      - ZITADEL_CLIENT_SECRET=${ZITADEL_CLIENT_SECRET}
      - ZITADEL_REDIRECT_URI=${ZITADEL_REDIRECT_URI:-https://tt-coaches.swisi.net/auth/callback}
      - ZITADEL_MANAGEMENT_API_URL=${ZITADEL_MANAGEMENT_API_URL:-https://tt-auth.swisi.net}
      - ZITADEL_MANAGEMENT_API_TOKEN=${ZITADEL_MANAGEMENT_API_TOKEN}
      - ZITADEL_DEFAULT_ROLE=${ZITADEL_DEFAULT_ROLE:-coach}
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

| Variable | Beschreibung | Standard | Erforderlich |
|----------|-------------|----------|--------------|
| `DOCKER_HUB_USERNAME` | Docker Hub Username | `swisi` | Nein |
| `IMAGE_TAG` | Image Version | `latest` | Nein |
| `SECRET_KEY` | Flask Secret Key | `change-me-in-production` | **Ja** (in Produktion ändern!) |
| `MAX_CONTENT_LENGTH` | Maximale Upload-Größe in Bytes | `524288000` (500MB) | Nein |
| `ZITADEL_ISSUER` | Zitadel Instance URL | `https://tt-auth.swisi.net` | **Ja** |
| `ZITADEL_CLIENT_ID` | OAuth2 Client ID | - | **Ja** |
| `ZITADEL_CLIENT_SECRET` | OAuth2 Client Secret | - | **Ja** |
| `ZITADEL_REDIRECT_URI` | OAuth2 Redirect URI | `https://tt-coaches.swisi.net/auth/callback` | **Ja** |
| `ZITADEL_MANAGEMENT_API_URL` | Management API URL | `https://tt-auth.swisi.net` | **Ja** |
| `ZITADEL_MANAGEMENT_API_TOKEN` | Management API Token | - | **Ja** |
| `ZITADEL_DEFAULT_ROLE` | Standard-Rolle für neue Benutzer | `coach` | Nein |

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

### Fehler: "Request Entity Too Large" oder "Datei zu groß"

**Ursache:** Backup-Datei überschreitet das Upload-Limit.

**Lösung:** 
1. Erhöhe `MAX_CONTENT_LENGTH` in den Umgebungsvariablen (in Bytes):
   ```yaml
   MAX_CONTENT_LENGTH=1048576000  # 1GB
   ```
2. Falls du einen Reverse Proxy (Nginx) verwendest, erhöhe auch dort das Limit:
   ```nginx
   client_max_body_size 1G;
   ```
3. In Portainer: Prüfe, ob es Container-spezifische Limits gibt

### Fehler: "Permission denied"

**Ursache:** Volume-Berechtigungen.

**Lösung:** Die Anwendung erstellt automatisch die benötigten Verzeichnisse beim Start.

### Container startet nicht

**Prüfe:**
1. Logs: `docker logs coaches-app`
2. Healthcheck: `docker inspect coaches-app`
3. Umgebungsvariablen in Portainer

### Fehler: "Not Found" bei Zertifikatsdateien

**Ursache:** Dateien existieren nicht im Volume oder Volume ist nicht richtig gemountet.

**Lösung:**
1. Prüfe, ob das Volume `coaches-uploads` existiert und Dateien enthält:
   ```bash
   docker volume inspect coaches-uploads
   docker exec coaches-app ls -la /app/app/static/uploads/certificates/
   ```
2. Nach einem Restore: Stelle sicher, dass die Dateien korrekt extrahiert wurden
3. Die Anwendung hat jetzt eine explizite Route zum Servieren von Dateien - nach dem nächsten Update sollte das Problem behoben sein
4. Falls das Problem weiterhin besteht, prüfe die Volume-Mount-Konfiguration in Portainer

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

