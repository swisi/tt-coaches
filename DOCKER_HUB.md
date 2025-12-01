# Docker Hub Deployment Anleitung

Anleitung zum Erstellen und Hochladen des CoachManager Docker-Images auf Docker Hub.

## 🐳 Voraussetzungen

1. **Docker installiert** und laufend
2. **Docker Hub Account** erstellt auf [hub.docker.com](https://hub.docker.com)
3. **Docker Hub Login** durchgeführt

## 📝 Schritt-für-Schritt Anleitung

### 1. Bei Docker Hub anmelden

```bash
docker login
```

Du wirst nach deinem Docker Hub Username und Passwort gefragt.

### 2. Docker-Image bauen

```bash
# Ersetze 'dein-username' mit deinem Docker Hub Username
docker build -t dein-username/coaches:latest .
```

**Beispiel:**
```bash
docker build -t swisi/coaches:latest .
```

### 3. Image testen (optional)

```bash
# Container lokal starten zum Testen
docker run -d \
  --name coaches-test \
  -p 3000:3000 \
  -e SECRET_KEY="test-secret-key" \
  dein-username/coaches:latest

# Testen
curl http://localhost:3000/auth/login

# Container stoppen und entfernen
docker stop coaches-test
docker rm coaches-test
```

### 4. Image zu Docker Hub pushen

```bash
docker push dein-username/coaches:latest
```

**Beispiel:**
```bash
docker push swisi/coaches:latest
```

### 5. Image mit Version taggen (empfohlen)

Für bessere Versionierung:

```bash
# Image mit Version taggen
docker tag dein-username/coaches:latest dein-username/coaches:1.0.0

# Version pushen
docker push dein-username/coaches:1.0.0

# Auch latest pushen
docker push dein-username/coaches:latest
```

## 🚀 Verwendung des Images von Docker Hub

Andere können dein Image jetzt verwenden:

```bash
# Image von Docker Hub pullen
docker pull dein-username/coaches:latest

# Container starten
docker run -d \
  --name coaches-app \
  -p 3000:3000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/uploads:/app/static/uploads \
  -e SECRET_KEY="dein-sicheres-secret-key" \
  dein-username/coaches:latest
```

## 📋 Docker Compose mit Docker Hub Image

Du kannst auch `docker-compose.yml` anpassen, um das Image von Docker Hub zu verwenden:

```yaml
version: '3.8'

services:
  web:
    image: dein-username/coaches:latest  # Statt 'build: .'
    container_name: coaches-app
    ports:
      - "3000:3000"
    environment:
      - SECRET_KEY=${SECRET_KEY:-change-me-in-production}
      - DATABASE_PATH=/app/data
      - DATABASE_URL=sqlite:///data/coaches.db
      - UPLOAD_BASE=/app
    volumes:
      - ./data:/app/data
      - ./uploads:/app/static/uploads
      - ./instance:/app/instance
    restart: unless-stopped
```

## 🔄 Image aktualisieren

Wenn du Änderungen gemacht hast:

```bash
# 1. Image neu bauen
docker build -t dein-username/coaches:latest .

# 2. Zu Docker Hub pushen
docker push dein-username/coaches:latest
```

## 📝 Docker Hub Repository Beschreibung

Auf Docker Hub kannst du eine README für dein Repository hinzufügen:

1. Gehe zu deinem Repository auf Docker Hub
2. Klicke auf "Edit description"
3. Füge eine Beschreibung hinzu:

```
CoachManager - American Football Coaching Management System

Eine Flask-Webanwendung zur Verwaltung von American Football Coaches, 
ihren Qualifikationen, Erfahrungen und Trainingsplänen.

Features:
- Dashboard mit Statistiken
- Profilverwaltung
- Zertifikate-Management
- Trainingspläne mit Live-Tracking
- Admin-Bereich
- Backup & Restore

Verwendung:
docker run -d -p 3000:3000 -e SECRET_KEY="your-key" dein-username/coaches:latest
```

## ⚙️ Automatisches Build auf Docker Hub (Optional)

Du kannst auch automatische Builds auf Docker Hub einrichten:

1. Gehe zu Docker Hub → Account Settings → Linked Accounts
2. Verbinde dein GitHub-Konto
3. Gehe zu deinem Repository → Builds
4. Klicke auf "Configure Automated Builds"
5. Wähle dein GitHub Repository aus
6. Docker Hub baut automatisch bei jedem Push

## 🎯 Zusammenfassung der Befehle

```bash
# 1. Login
docker login

# 2. Image bauen
docker build -t dein-username/coaches:latest .

# 3. Pushen
docker push dein-username/coaches:latest

# 4. Optional: Mit Version
docker tag dein-username/coaches:latest dein-username/coaches:1.0.0
docker push dein-username/coaches:1.0.0
```

