# Multi-stage build für optimiertes Image
FROM python:3.12-slim as builder

WORKDIR /app

# Installiere Build-Abhängigkeiten
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Kopiere requirements und installiere Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Produktions-Stage
FROM python:3.12-slim

WORKDIR /app

# Installiere Runtime-Abhängigkeiten
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Kopiere Python-Pakete vom Builder
COPY --from=builder /root/.local /root/.local

# Stelle sicher, dass Python die lokal installierten Pakete findet
ENV PATH=/root/.local/bin:$PATH

# Kopiere Anwendungsdateien
COPY . .

# Erstelle notwendige Verzeichnisse
RUN mkdir -p app/static/uploads/certificates instance data

# Setze Umgebungsvariablen
ENV FLASK_APP=run.py
ENV PYTHONUNBUFFERED=1

# Exponiere Port
EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:3000/auth/login')" || exit 1

# Starte mit Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "run:app"]

