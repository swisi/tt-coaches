"""
Backup-Utilities für die Anwendung
"""
import os
import zipfile
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import pymysql
from config import Config


def parse_database_url(db_url):
    """Parst die SQLAlchemy-Datenbank-URL und extrahiert Verbindungsdaten"""
    parsed = urlparse(db_url.replace('mysql+pymysql://', 'mysql://'))
    
    return {
        'host': parsed.hostname,
        'port': parsed.port or 3306,
        'user': parsed.username,
        'password': parsed.password,
        'database': parsed.path.lstrip('/').split('?')[0]
    }


def create_database_backup(output_path):
    """
    Erstellt ein SQL-Dump der Datenbank
    """
    db_url = Config.SQLALCHEMY_DATABASE_URI
    db_config = parse_database_url(db_url)
    
    try:
        # Verbinde zur Datenbank
        connection = pymysql.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            charset='utf8mb4'
        )
        
        # Erstelle SQL-Dump
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"-- TT-Coaches Datenbank Backup\n")
            f.write(f"-- Erstellt am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- Datenbank: {db_config['database']}\n\n")
            f.write(f"SET FOREIGN_KEY_CHECKS=0;\n\n")
            
            cursor = connection.cursor()
            
            # Hole alle Tabellen
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            
            for table in tables:
                f.write(f"-- Struktur für Tabelle: {table}\n")
                
                # Hole CREATE TABLE Statement
                cursor.execute(f"SHOW CREATE TABLE `{table}`")
                create_table = cursor.fetchone()[1]
                f.write(f"DROP TABLE IF EXISTS `{table}`;\n")
                f.write(f"{create_table};\n\n")
                
                # Hole Daten
                cursor.execute(f"SELECT * FROM `{table}`")
                columns = [col[0] for col in cursor.description]
                
                # Hole alle Zeilen
                rows = cursor.fetchall()
                if rows:
                    f.write(f"-- Daten für Tabelle: {table}\n")
                    f.write(f"LOCK TABLES `{table}` WRITE;\n")
                    
                    for row in rows:
                        values = []
                        for value in row:
                            if value is None:
                                values.append('NULL')
                            elif isinstance(value, (int, float)):
                                values.append(str(value))
                            else:
                                # Escape für SQL (manuell)
                                value_str = str(value)
                                # Escape Sonderzeichen für SQL
                                escaped_value = value_str.replace("\\", "\\\\").replace("'", "''").replace("\n", "\\n").replace("\r", "\\r")
                                values.append(f"'{escaped_value}'")
                        
                        columns_str = ', '.join([f"`{col}`" for col in columns])
                        values_str = ', '.join(values)
                        f.write(f"INSERT INTO `{table}` ({columns_str}) VALUES ({values_str});\n")
                    
                    f.write(f"UNLOCK TABLES;\n\n")
            
            f.write(f"SET FOREIGN_KEY_CHECKS=1;\n")
        
        connection.close()
        return True
    except Exception as e:
        print(f"Fehler beim Erstellen des Datenbank-Backups: {e}")
        return False


def create_files_backup(output_path):
    """
    Erstellt ein ZIP-Archiv aller Upload-Dateien
    """
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Füge alle Dateien aus den Upload-Verzeichnissen hinzu
            folders = [
                ('certificates', Config.CERTIFICATES_FOLDER),
                ('cv', Config.CV_FOLDER),
                ('profile_images', Config.PROFILE_IMAGES_FOLDER)
            ]
            
            for folder_name, folder_path in folders:
                if folder_path.exists():
                    for root, dirs, files in os.walk(folder_path):
                        for file in files:
                            file_path = Path(root) / file
                            # Relative Pfad für ZIP (ohne absoluten Pfad)
                            arcname = f"uploads/{folder_name}/{file_path.name}"
                            zipf.write(file_path, arcname)
        
        return True
    except Exception as e:
        print(f"Fehler beim Erstellen des Datei-Backups: {e}")
        return False


def create_full_backup(backup_dir=None):
    """
    Erstellt ein vollständiges Backup (Datenbank + Dateien) als ZIP-Archiv
    Returns: (success: bool, backup_path: str, error_message: str)
    """
    if backup_dir is None:
        backup_dir = Path(__file__).parent.parent / 'backups'
    
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(exist_ok=True)
    
    # Erstelle Backup-Dateiname mit Zeitstempel
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'tt_coaches_backup_{timestamp}.zip'
    backup_path = backup_dir / backup_filename
    
    try:
        # Temporäres Verzeichnis für Backups
        temp_dir = backup_dir / f'temp_{timestamp}'
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Erstelle Datenbank-Backup
            db_backup_path = temp_dir / 'database.sql'
            if not create_database_backup(db_backup_path):
                return False, None, "Fehler beim Erstellen des Datenbank-Backups"
            
            # Erstelle ZIP mit allem
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Füge Datenbank-Backup hinzu
                zipf.write(db_backup_path, 'database.sql')
                
                # Füge alle Upload-Dateien hinzu
                folders = [
                    ('certificates', Config.CERTIFICATES_FOLDER),
                    ('cv', Config.CV_FOLDER),
                    ('profile_images', Config.PROFILE_IMAGES_FOLDER)
                ]
                
                for folder_name, folder_path in folders:
                    if folder_path.exists():
                        for root, dirs, files in os.walk(folder_path):
                            for file in files:
                                file_path = Path(root) / file
                                # Relative Pfad für ZIP
                                arcname = f"uploads/{folder_name}/{file_path.name}"
                                zipf.write(file_path, arcname)
        
        finally:
            # Lösche temporäres Verzeichnis
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        
        return True, str(backup_path), None
    
    except Exception as e:
        error_msg = f"Fehler beim Erstellen des Backups: {str(e)}"
        return False, None, error_msg

