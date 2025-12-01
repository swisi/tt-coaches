"""
Backup & Restore Funktionen für die CoachManager Anwendung
"""
from datetime import datetime, date, time
from app import db
from app.models import User, Certificate, Experience, TrainingPlan, TrainingActivity
from flask import current_app
import json
import io
import os
import zipfile
import shutil

def export_backup():
    """
    Exportiert alle Daten aus der Datenbank als JSON
    """
    backup_data = {
        'version': '1.0',
        'export_date': datetime.now().isoformat(),
        'users': [],
        'certificates': [],
        'experiences': [],
        'training_plans': [],
        'training_activities': []
    }
    
    # Exportiere alle Benutzer
    users = User.query.all()
    for user in users:
        user_data = {
            'id': user.id,
            'email': user.email,
            'password_hash': user.password_hash,  # Wichtig: Passwörter werden mit exportiert
            'full_name': user.full_name,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'license_number': user.license_number,
            'mobile_phone': user.mobile_phone,
            'address': user.address,
            'zip_code': user.zip_code,
            'city': user.city,
            'birth_date': user.birth_date.isoformat() if user.birth_date else None,
            'team': user.team,
            'is_admin': user.is_admin,
            'created_date': user.created_date.isoformat() if user.created_date else None,
            'updated_date': user.updated_date.isoformat() if user.updated_date else None
        }
        backup_data['users'].append(user_data)
    
    # Exportiere alle Zertifikate
    certificates = Certificate.query.all()
    for cert in certificates:
        cert_data = {
            'id': cert.id,
            'user_id': cert.user_id,
            'title': cert.title,
            'organization': cert.organization,
            'acquisition_date': cert.acquisition_date.isoformat() if cert.acquisition_date else None,
            'valid_until': cert.valid_until.isoformat() if cert.valid_until else None,
            'file_url': cert.file_url,
            'created_date': cert.created_date.isoformat() if cert.created_date else None,
            'updated_date': cert.updated_date.isoformat() if cert.updated_date else None
        }
        backup_data['certificates'].append(cert_data)
    
    # Exportiere alle Erfahrungen
    experiences = Experience.query.all()
    for exp in experiences:
        exp_data = {
            'id': exp.id,
            'user_id': exp.user_id,
            'start_year': exp.start_year,
            'end_year': exp.end_year,
            'team': exp.team,
            'position': exp.position,
            'created_date': exp.created_date.isoformat() if exp.created_date else None,
            'updated_date': exp.updated_date.isoformat() if exp.updated_date else None
        }
        backup_data['experiences'].append(exp_data)
    
    # Exportiere alle Trainingspläne
    training_plans = TrainingPlan.query.all()
    for plan in training_plans:
        plan_data = {
            'id': plan.id,
            'title': plan.title,
            'team_name': plan.team_name,
            'start_date': plan.start_date.isoformat() if plan.start_date else None,
            'end_date': plan.end_date.isoformat() if plan.end_date else None,
            'weekday': plan.weekday,
            'start_time': plan.start_time.isoformat() if plan.start_time else None,
            'dresscode': plan.dresscode,
            'focus': plan.focus,
            'goals': plan.goals,
            'sort_order': plan.sort_order,
            'created_date': plan.created_date.isoformat() if plan.created_date else None,
            'updated_date': plan.updated_date.isoformat() if plan.updated_date else None
        }
        backup_data['training_plans'].append(plan_data)
    
    # Exportiere alle Trainingsaktivitäten
    activities = TrainingActivity.query.all()
    for activity in activities:
        activity_data = {
            'id': activity.id,
            'plan_id': activity.plan_id,
            'time_from': activity.time_from.isoformat() if activity.time_from else None,
            'time_to': activity.time_to.isoformat() if activity.time_to else None,
            'duration_minutes': activity.duration_minutes,
            'activity_name': activity.activity_name,
            'activity_type': activity.activity_type,
            'group_activities': activity.group_activities,
            'groups': activity.groups,
            'notes': activity.notes,
            'order': activity.order,
            'created_date': activity.created_date.isoformat() if activity.created_date else None,
            'updated_date': activity.updated_date.isoformat() if activity.updated_date else None
        }
        backup_data['training_activities'].append(activity_data)
    
    return json.dumps(backup_data, indent=2, ensure_ascii=False)

def create_backup_zip():
    """
    Erstellt ein ZIP-Archiv mit JSON-Daten und allen hochgeladenen Dateien
    """
    backup_json = export_backup()
    
    # Erstelle ZIP im Speicher
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Füge JSON-Daten hinzu
        zip_file.writestr('backup.json', backup_json)
        
        # Füge alle hochgeladenen Zertifikatsdateien hinzu
        upload_folder = current_app.config['UPLOAD_FOLDER']
        current_app.logger.info(f"Backup: Suche Dateien in {upload_folder}")
        
        if os.path.exists(upload_folder):
            files_added = 0
            upload_base_dir = os.path.dirname(upload_folder)  # z.B. /app/static/uploads
            
            try:
                for root, dirs, files in os.walk(upload_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        # Prüfe ob Datei wirklich existiert und lesbar ist
                        if not os.path.isfile(file_path):
                            current_app.logger.warning(f"Backup: Überspringe {file_path} (keine Datei)")
                            continue
                        
                        # Relativer Pfad innerhalb des ZIPs
                        # z.B. upload_folder = /app/static/uploads/certificates
                        #      upload_base_dir = /app/static/uploads
                        #      file_path = /app/static/uploads/certificates/file.pdf
                        #      arcname = certificates/file.pdf
                        try:
                            arcname = os.path.relpath(file_path, upload_base_dir)
                            zip_file.write(file_path, arcname=f'uploads/{arcname}')
                            files_added += 1
                            current_app.logger.debug(f"Backup: Datei hinzugefügt: {file_path} -> uploads/{arcname}")
                        except Exception as e:
                            current_app.logger.error(f"Backup: Fehler beim Hinzufügen von {file_path}: {e}")
                            continue
                
                if files_added == 0:
                    current_app.logger.warning(f"Backup: Keine Dateien im Upload-Ordner gefunden: {upload_folder}")
                else:
                    current_app.logger.info(f"Backup: {files_added} Dateien zum ZIP hinzugefügt")
            except Exception as e:
                current_app.logger.error(f"Backup: Fehler beim Durchsuchen des Upload-Ordners: {e}")
        else:
            current_app.logger.warning(f"Backup: Upload-Ordner existiert nicht: {upload_folder}")
    
    zip_buffer.seek(0)
    return zip_buffer

def restore_backup_from_zip(zip_file, clear_existing=False):
    """
    Stellt Daten aus einem ZIP-Backup wieder her
    
    Args:
        zip_file: Geöffnete ZIP-Datei
        clear_existing: Wenn True, werden alle bestehenden Daten gelöscht
    
    Returns:
        Tuple (success: bool, message: str, stats: dict)
    """
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            # Extrahiere JSON-Daten
            if 'backup.json' not in zip_ref.namelist():
                return False, "Keine backup.json im ZIP-Archiv gefunden.", {}
            
            backup_json = zip_ref.read('backup.json').decode('utf-8')
            
            # Importiere Daten
            success, message, stats = import_backup(backup_json, clear_existing=clear_existing)
            
            if not success:
                return False, message, stats
            
            # Extrahiere Dateien
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            
            # Extrahiere alle Dateien aus dem uploads/ Ordner
            files_restored = 0
            for file_info in zip_ref.filelist:
                if file_info.filename.startswith('uploads/') and not file_info.is_dir():
                    # Entferne 'uploads/' Präfix
                    relative_path = file_info.filename[len('uploads/'):]
                    target_path = os.path.join(upload_folder, relative_path)
                    
                    # Stelle sicher, dass das Verzeichnis existiert
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    
                    # Extrahiere Datei
                    with zip_ref.open(file_info.filename) as source:
                        with open(target_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
                    files_restored += 1
            
            message += f" {files_restored} Dateien wiederhergestellt."
            stats['files'] = files_restored
            
            return True, message, stats
            
    except Exception as e:
        db.session.rollback()
        return False, f"Fehler beim Wiederherstellen aus ZIP: {str(e)}", {}

def import_backup(backup_json, clear_existing=False):
    """
    Importiert Daten aus einem Backup-JSON
    
    Args:
        backup_json: JSON-String mit den Backup-Daten
        clear_existing: Wenn True, werden alle bestehenden Daten gelöscht
    
    Returns:
        Tuple (success: bool, message: str, stats: dict)
    """
    try:
        backup_data = json.loads(backup_json)
        
        # Helper-Funktionen für Datum/Zeit-Konvertierung
        def parse_date(date_str):
            """Konvertiert einen String zu einem date-Objekt"""
            if not date_str:
                return None
            try:
                if isinstance(date_str, str):
                    if len(date_str) == 10:  # YYYY-MM-DD Format
                        return date.fromisoformat(date_str)
                    else:
                        # Falls datetime String, extrahiere nur das Datum
                        return datetime.fromisoformat(date_str).date()
                return date_str
            except (ValueError, AttributeError):
                try:
                    return datetime.fromisoformat(date_str).date()
                except:
                    return None
        
        def parse_time(time_str):
            """Konvertiert einen String zu einem time-Objekt"""
            if not time_str:
                return None
            try:
                if isinstance(time_str, str):
                    # Versuche zuerst time.fromisoformat (für reine Zeitstrings wie HH:MM:SS)
                    if 'T' not in time_str and len(time_str) <= 8:
                        return time.fromisoformat(time_str)
                    else:
                        # Falls datetime String, extrahiere nur die Zeit
                        return datetime.fromisoformat(time_str).time()
                return time_str
            except (ValueError, AttributeError):
                try:
                    return datetime.fromisoformat(time_str).time()
                except:
                    return None
        
        stats = {
            'users': 0,
            'certificates': 0,
            'experiences': 0,
            'training_plans': 0,
            'training_activities': 0
        }
        
        if clear_existing:
            # Lösche alle bestehenden Daten (in umgekehrter Reihenfolge wegen Foreign Keys)
            TrainingActivity.query.delete()
            TrainingPlan.query.delete()
            Experience.query.delete()
            Certificate.query.delete()
            User.query.delete()
            db.session.commit()
        
        # Importiere Benutzer
        if 'users' in backup_data:
            for user_data in backup_data['users']:
                # Prüfe ob Benutzer bereits existiert
                existing_user = User.query.filter_by(email=user_data['email']).first()
                if existing_user and not clear_existing:
                    continue  # Überspringe existierende Benutzer
                
                user = User(
                    email=user_data['email'],
                    password_hash=user_data.get('password_hash', ''),
                    full_name=user_data.get('full_name'),
                    first_name=user_data.get('first_name'),
                    last_name=user_data.get('last_name'),
                    license_number=user_data.get('license_number'),
                    mobile_phone=user_data.get('mobile_phone'),
                    address=user_data.get('address'),
                    zip_code=user_data.get('zip_code'),
                    city=user_data.get('city'),
                    birth_date=parse_date(user_data.get('birth_date')),
                    team=user_data.get('team'),
                    is_admin=user_data.get('is_admin', False)
                )
                db.session.add(user)
                stats['users'] += 1
        
        db.session.flush()  # Um IDs zu erhalten
        
        # Erstelle Mapping von alter E-Mail zu neuer User-ID
        email_to_user_id = {}
        for user in User.query.all():
            email_to_user_id[user.email] = user.id
        
        # Importiere Zertifikate
        if 'certificates' in backup_data:
            for cert_data in backup_data['certificates']:
                # Finde Benutzer per E-Mail aus dem Backup
                user_email = None
                if 'users' in backup_data and cert_data['user_id'] <= len(backup_data['users']):
                    user_email = backup_data['users'][cert_data['user_id']-1]['email']
                
                if not user_email or user_email not in email_to_user_id:
                    continue
                
                user_id = email_to_user_id[user_email]
                
                cert = Certificate(
                    user_id=user_id,
                    title=cert_data['title'],
                    organization=cert_data['organization'],
                    acquisition_date=parse_date(cert_data.get('acquisition_date')),
                    valid_until=parse_date(cert_data.get('valid_until')),
                    file_url=cert_data.get('file_url')
                )
                db.session.add(cert)
                stats['certificates'] += 1
        
        # Importiere Erfahrungen
        if 'experiences' in backup_data:
            for exp_data in backup_data['experiences']:
                # Finde Benutzer per E-Mail aus dem Backup
                user_email = None
                if 'users' in backup_data and exp_data['user_id'] <= len(backup_data['users']):
                    user_email = backup_data['users'][exp_data['user_id']-1]['email']
                
                if not user_email or user_email not in email_to_user_id:
                    continue
                
                user_id = email_to_user_id[user_email]
                
                exp = Experience(
                    user_id=user_id,
                    start_year=exp_data['start_year'],
                    end_year=exp_data.get('end_year'),
                    team=exp_data['team'],
                    position=exp_data['position']
                )
                db.session.add(exp)
                stats['experiences'] += 1
        
        # Importiere Trainingspläne
        plan_id_mapping = {}  # Alte ID -> Neue ID
        if 'training_plans' in backup_data:
            for plan_data in backup_data['training_plans']:
                old_id = plan_data['id']
                plan = TrainingPlan(
                    title=plan_data['title'],
                    team_name=plan_data['team_name'],
                    start_date=parse_date(plan_data.get('start_date')),
                    end_date=parse_date(plan_data.get('end_date')),
                    weekday=plan_data['weekday'],
                    start_time=parse_time(plan_data.get('start_time')),
                    dresscode=plan_data.get('dresscode'),
                    focus=plan_data.get('focus'),
                    goals=plan_data.get('goals'),
                    sort_order=plan_data.get('sort_order', 0)
                )
                db.session.add(plan)
                db.session.flush()
                plan_id_mapping[old_id] = plan.id
                stats['training_plans'] += 1
        
        # Importiere Trainingsaktivitäten
        if 'training_activities' in backup_data:
            for activity_data in backup_data['training_activities']:
                new_plan_id = plan_id_mapping.get(activity_data['plan_id'])
                if not new_plan_id:
                    continue
                
                activity = TrainingActivity(
                    plan_id=new_plan_id,
                    time_from=parse_time(activity_data.get('time_from')),
                    time_to=parse_time(activity_data.get('time_to')),
                    duration_minutes=activity_data['duration_minutes'],
                    activity_name=activity_data['activity_name'],
                    activity_type=activity_data['activity_type'],
                    group_activities=activity_data.get('group_activities'),
                    groups=activity_data.get('groups'),
                    notes=activity_data.get('notes'),
                    order=activity_data.get('order', 0)
                )
                db.session.add(activity)
                stats['training_activities'] += 1
        
        db.session.commit()
        
        message = f"Backup erfolgreich importiert: {stats['users']} Benutzer, {stats['certificates']} Zertifikate, {stats['experiences']} Erfahrungen, {stats['training_plans']} Trainingspläne, {stats['training_activities']} Aktivitäten"
        return True, message, stats
        
    except Exception as e:
        db.session.rollback()
        return False, f"Fehler beim Importieren: {str(e)}", {}

