# GitHub Actions

## Docker Build Workflow

Diese Workflow erlaubt es, das Docker-Image manuell zu builden und zu Docker Hub zu pushen.

### Setup

1. **Docker Hub Secrets hinzufügen:**
   - Gehe zu deinem GitHub Repository
   - Settings → Secrets and variables → Actions
   - Klicke auf "New repository secret"
   - Füge folgende Secrets hinzu:
     - `DOCKER_HUB_USERNAME`: Dein Docker Hub Username
     - `DOCKER_HUB_TOKEN`: Dein Docker Hub Access Token (nicht Passwort!)

2. **Docker Hub Access Token erstellen:**
   - Gehe zu [hub.docker.com](https://hub.docker.com)
   - Account Settings → Security → New Access Token
   - Erstelle einen Token mit "Read & Write" Berechtigung
   - Kopiere den Token (wird nur einmal angezeigt!)

### Verwendung

1. Gehe zu deinem GitHub Repository
2. Klicke auf "Actions" Tab
3. Wähle "Build and Push Docker Image" Workflow
4. Klicke auf "Run workflow"
5. Wähle Branch (normalerweise "main")
6. Optionale Eingaben:
   - **Version**: Version-Tag (z.B. "1.0.0", Standard: "latest")
   - **Push to Docker Hub**: Ob das Image gepusht werden soll (Standard: true)
7. Klicke auf "Run workflow"

### Workflow-Schritte

1. ✅ Code auschecken
2. ✅ Docker Buildx Setup
3. ✅ Bei Docker Hub anmelden (wenn Push aktiviert)
4. ✅ Docker-Image bauen
5. ✅ Image zu Docker Hub pushen (wenn aktiviert)

### Beispiel

**Nur bauen (ohne Push):**
- Version: `test`
- Push to Docker Hub: `false`

**Bauen und pushen:**
- Version: `1.0.0`
- Push to Docker Hub: `true`

Das Image wird dann verfügbar sein als:
- `dein-username/coaches:1.0.0`
- `dein-username/coaches:latest` (wenn main branch)

