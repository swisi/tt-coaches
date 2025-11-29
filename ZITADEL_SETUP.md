# Zitadel Integration Setup

Diese Anwendung verwendet Zitadel für die Benutzerauthentifizierung und -verwaltung.

## Konfiguration

### 1. Zitadel-Instanz einrichten

Stelle sicher, dass du eine selbst gehostete Zitadel-Instanz hast und die folgenden Informationen kennst:
- Issuer URL (z.B. `https://zitadel.example.com`)
- Client ID und Client Secret für OAuth2
- Management API Token (Service Account Token)

### 2. OAuth2 Application in Zitadel erstellen

1. Gehe zu deiner Zitadel-Instanz
2. Erstelle eine neue OAuth2 Application
3. Wähle "Web Application" als Application Type
4. Setze die Redirect URI auf: `http://localhost:5000/auth/callback` (oder deine Produktions-URL)
5. Notiere dir die Client ID und Client Secret

Client-ID: 348824518581616643
Client-Sec: b3583K3Gudad6JpU3qlrM3HDHWq1BhJU7jOkh4OIzQExcFH4vVEoOIoOU1Tuq7cz

### 3. Management API Service Account erstellen

1. Erstelle einen Service Account in Zitadel
2. Weise dem Service Account die Berechtigung zum Erstellen von Benutzern zu
3. Generiere einen API Token für den Service Account
4. Notiere dir den Token

Token: D4rOw_p3PemBeN5iNlsSwIC39lLE0JM4wV3bhxXLFUXf3wabHWq_0AMvtrrDoYkmK6iWPpc

### 4. Umgebungsvariablen setzen

Setze die folgenden Umgebungsvariablen:

```bash
# Zitadel OAuth2/OIDC Einstellungen
export ZITADEL_ISSUER="https://your-zitadel-instance.com"
export ZITADEL_CLIENT_ID="your-client-id"
export ZITADEL_CLIENT_SECRET="your-client-secret"
export ZITADEL_REDIRECT_URI="http://localhost:5000/auth/callback"

# Zitadel Management API (für Benutzerregistrierung)
export ZITADEL_MANAGEMENT_API_URL="https://your-zitadel-instance.com"
export ZITADEL_MANAGEMENT_API_TOKEN="your-service-account-token"

# Optional: Standard-Rolle für neue Benutzer
export ZITADEL_DEFAULT_ROLE="coach"
```

Oder erstelle eine `.env` Datei:

```env
ZITADEL_ISSUER=https://your-zitadel-instance.com
ZITADEL_CLIENT_ID=your-client-id
ZITADEL_CLIENT_SECRET=your-client-secret
ZITADEL_REDIRECT_URI=http://localhost:5000/auth/callback
ZITADEL_MANAGEMENT_API_URL=https://your-zitadel-instance.com
ZITADEL_MANAGEMENT_API_TOKEN=your-service-account-token
ZITADEL_DEFAULT_ROLE=coach
```

### 5. Datenbank-Migration durchführen

Die Datenbank-Struktur wurde angepasst. Führe eine Migration durch:

```bash
flask db migrate -m "Add Zitadel integration"
flask db upgrade
```

## Funktionsweise

### Login
- Benutzer klicken auf "Mit Zitadel anmelden"
- Sie werden zu Zitadel weitergeleitet
- Nach erfolgreicher Authentifizierung werden sie zurück zur Anwendung geleitet
- Die Anwendung erstellt automatisch einen lokalen Benutzer-Eintrag, falls noch nicht vorhanden

### Registrierung
- Neue Benutzer registrieren sich über das Signup-Formular
- Der Benutzer wird in Zitadel erstellt (über Management API)
- Ein lokaler Benutzer-Eintrag wird in der Datenbank erstellt
- Der Benutzer erhält automatisch die Standard-Rolle (falls konfiguriert)

### Passwort-Verwaltung
- Passwörter werden vollständig von Zitadel verwaltet
- Benutzer können ihre Passwörter direkt in Zitadel ändern
- Die Anwendung speichert keine Passwörter mehr lokal

## Migration bestehender Benutzer

Bestehende Benutzer mit lokalem Passwort können weiterhin funktionieren, aber:
- Sie sollten sich über Zitadel anmelden
- Beim ersten Login über Zitadel wird ihr lokaler Account mit der Zitadel User ID verknüpft
- Das lokale Passwort wird dann nicht mehr verwendet

## Fehlerbehebung

### "Zitadel Management API nicht konfiguriert"
- Stelle sicher, dass `ZITADEL_MANAGEMENT_API_URL` und `ZITADEL_MANAGEMENT_API_TOKEN` gesetzt sind
- Prüfe, ob der Service Account Token gültig ist und die richtigen Berechtigungen hat

### "Fehler beim Erstellen des Benutzers in Zitadel"
- Prüfe die Zitadel-Logs für detaillierte Fehlermeldungen
- Stelle sicher, dass die Management API URL korrekt ist
- Prüfe, ob der Service Account die Berechtigung zum Erstellen von Benutzern hat

### OAuth2 Callback-Fehler
- Stelle sicher, dass die Redirect URI in Zitadel korrekt konfiguriert ist
- Prüfe, ob Client ID und Client Secret korrekt sind
- Stelle sicher, dass die Issuer URL korrekt ist

## API-Endpunkte

Die Anwendung verwendet folgende Zitadel-Endpunkte:

- **OAuth2/OIDC**: `{ZITADEL_ISSUER}/.well-known/openid-configuration`
- **Management API**: `{ZITADEL_MANAGEMENT_API_URL}/management/v1/users/human/_import`

Die genaue API-Struktur kann je nach Zitadel-Version variieren. Konsultiere die Zitadel-Dokumentation für deine Version.

