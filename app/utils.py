"""
Hilfsfunktionen für die Anwendung
"""
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from pathlib import Path

def allowed_file(filename):
    """Prüft ob Dateiname erlaubt ist"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_uploaded_file(file, folder_type, prefix=''):
    """Speichert eine hochgeladene Datei sicher
    
    Args:
        file: Die hochzuladende Datei
        folder_type: 'CV', 'CERTIFICATES' oder 'PROFILE_IMAGES'
        prefix: Präfix für den Dateinamen
    """
    if file and allowed_file(file.filename):
        # Generiere eindeutigen Dateinamen
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{prefix}_{uuid.uuid4().hex[:8]}.{ext}"
        
        # Bestimme Zielverzeichnis
        if folder_type == 'CV':
            upload_folder = Path(current_app.config['CV_FOLDER'])
        elif folder_type == 'CERTIFICATES':
            upload_folder = Path(current_app.config['CERTIFICATES_FOLDER'])
        elif folder_type == 'PROFILE_IMAGES':
            upload_folder = Path(current_app.config['PROFILE_IMAGES_FOLDER'])
        else:
            upload_folder = Path(current_app.config['UPLOAD_FOLDER'])
        
        file_path = upload_folder / unique_filename
        
        file.save(str(file_path))
        # Normalisiere Pfad zu Forward-Slashes für URLs (Windows-kompatibel)
        relative_path = file_path.relative_to(current_app.config['UPLOAD_FOLDER'])
        return str(relative_path).replace('\\', '/')
    
    return None

def delete_file(file_path):
    """Löscht eine Datei aus dem Upload-Verzeichnis"""
    if file_path:
        # Normalisiere Pfad (konvertiere Backslashes zu Forward-Slashes)
        normalized_path = str(file_path).replace('\\', '/')
        full_path = Path(current_app.config['UPLOAD_FOLDER']) / normalized_path
        if full_path.exists():
            try:
                full_path.unlink()
                return True
            except Exception:
                return False
    return False

