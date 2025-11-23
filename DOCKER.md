# Docker Deployment für CoachManager

Anleitung zur Bereitstellung der CoachManager-Anwendung in Docker-Containern.

## 🐳 Voraussetzungen

- Docker installiert
- Docker Compose installiert (optional, aber empfohlen)

## 🚀 Schnellstart

### Mit Docker Compose (empfohlen)

1. **Umgebungsvariablen setzen** (optional):
```bash
export SECRET_KEY="dein-sicheres-secret-key"
```

2. **Container starten**:
```bash
docker-compose up -d
```

3. **Anwendung aufrufen**:
```
http://localhost:3000
```

4. **Logs ansehen**:
```bash
docker-compose logs -f
```

5. **Container stoppen**:
```bash
docker-compose down
```

### Mit Docker direkt

1. **Image bauen**:
```bash
docker build -t coaches-app .
```

2. **Container starten**:
```bash
docker run -d \
  --name coaches-app \
  -p 3000:3000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/uploads:/app/app/static/uploads \
  -e SECRET_KEY="dein-sicheres-secret-key" \
  coaches-app
```

## 📁 Volumes

Die folgenden Verzeichnisse werden als Volumes gemountet:

- `./data` - Datenbank-Dateien (coaches.db)
- `./uploads` - Hochgeladene Dateien (Zertifikate)
- `./instance` - Flask-Instance-Konfiguration

## 🔧 Umgebungsvariablen

| Variable | Beschreibung | Standard |
|----------|-------------|----------|
| `SECRET_KEY` | Flask Secret Key | `change-me-in-production` |
| `DATABASE_URL` | Datenbank-URI | `sqlite:///data/coaches.db` |
| `DATABASE_PATH` | Pfad für SQLite-Datenbank | `/app/data` |
| `UPLOAD_BASE` | Basis-Pfad für Uploads | `/app` |

## 📊 Datenbank-Migrationen

Bei der ersten Ausführung wird die Datenbank automatisch erstellt. Für Migrationen:

```bash
docker-compose exec web flask db upgrade
```

## 🔄 Backup & Restore

Backups können über die Web-Oberfläche erstellt werden (Admin-Bereich → Backup & Restore).

Backups werden im Container gespeichert. Um sie zu sichern:

```bash
docker cp coaches-app:/app/data/backup.zip ./backup.zip
```

## 🛠️ Wartung

### Logs ansehen
```bash
docker-compose logs -f web
```

### In Container einsteigen
```bash
docker-compose exec web bash
```

### Datenbank zurücksetzen
```bash
docker-compose down
rm -rf data/uploads
docker-compose up -d
```

## 🚢 Produktions-Deployment

Für Produktion:

1. **Sichere SECRET_KEY setzen**:
```bash
export SECRET_KEY=$(openssl rand -hex 32)
```

2. **Reverse Proxy konfigurieren** (Nginx/Traefik):
```nginx
server {
    listen 80;
    server_name coaches.example.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **HTTPS aktivieren** (Let's Encrypt)

4. **Regelmäßige Backups** einrichten

## 📝 Hinweise

- Die Datenbank wird in `./data/coaches.db` gespeichert
- Upload-Dateien werden in `./uploads/` gespeichert
- Bei Container-Neustart bleiben alle Daten erhalten (dank Volumes)
- Für Produktion: Verwende eine externe Datenbank (PostgreSQL) statt SQLite

