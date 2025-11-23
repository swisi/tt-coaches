import os
from werkzeug.utils import secure_filename
from datetime import datetime, time, timedelta
from flask import current_app

def allowed_file(filename):
    """Prüft ob die Dateiendung erlaubt ist"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_certificate_file(file):
    """Speichert eine hochgeladene Zertifikatsdatei"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Eindeutigen Dateinamen erstellen
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        filename = f"{timestamp}_{name}{ext}"
        
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Relative URL zurückgeben
        return f"/static/uploads/certificates/{filename}"
    return None

def calculate_activity_times(plan, activities, new_activity=None):
    """
    Berechnet die Zeiten für Aktivitäten basierend auf dem Plan-Startzeitpunkt.
    Prepractice-Aktivitäten werden rückwärts berechnet, andere vorwärts.
    """
    from app.models import TrainingActivity
    
    # Alle Aktivitäten sortieren
    all_activities = list(activities.order_by(TrainingActivity.order).all())
    
    if new_activity:
        # Temporär hinzufügen für Berechnung
        all_activities.append(new_activity)
        all_activities.sort(key=lambda x: x.order)
    
    # Prepractice-Aktivitäten finden
    prepractice_activities = [a for a in all_activities if a.activity_type == 'prepractice']
    regular_activities = [a for a in all_activities if a.activity_type != 'prepractice']
    
    # Prepractice rückwärts berechnen
    current_time = datetime.combine(datetime.today(), plan.start_time)
    for activity in reversed(prepractice_activities):
        duration = timedelta(minutes=activity.duration_minutes)
        current_time = current_time - duration
        activity.time_from = current_time.time()
        activity.time_to = (current_time + duration).time()
    
    # Reguläre Aktivitäten vorwärts berechnen
    current_time = datetime.combine(datetime.today(), plan.start_time)
    for activity in regular_activities:
        activity.time_from = current_time.time()
        duration = timedelta(minutes=activity.duration_minutes)
        current_time = current_time + duration
        activity.time_to = current_time.time()
    
    return all_activities

def get_next_start_time(plan, activities):
    """Gibt die nächste Startzeit für eine neue Aktivität zurück"""
    from app.models import TrainingActivity
    
    if not activities.count():
        return plan.start_time
    
    last_activity = activities.order_by(TrainingActivity.order.desc()).first()
    if last_activity:
        return last_activity.time_to
    
    return plan.start_time

def check_activity_status(activity, plan):
    """
    Prüft den Status einer Aktivität (JETZT, IN 2 MIN, oder normal)
    Gibt zurück: 'now', 'soon', oder None
    """
    if not plan.is_active_today():
        return None
    
    now = datetime.now()
    today = now.date()
    current_time = now.time()
    
    # Kombiniere Datum und Zeit für Vergleich
    from_time = datetime.combine(today, activity.time_from)
    to_time = datetime.combine(today, activity.time_to)
    now_dt = datetime.combine(today, current_time)
    
    # Prüfe ob Aktivität gerade läuft
    if from_time <= now_dt < to_time:
        return 'now'
    
    # Prüfe ob Aktivität in 2 Minuten startet
    two_minutes = timedelta(minutes=2)
    if from_time - two_minutes <= now_dt < from_time:
        return 'soon'
    
    return None

def format_time_delta(td):
    """Formatiert ein timedelta-Objekt als lesbare Zeitspanne"""
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}min"
    elif minutes > 0:
        return f"{minutes}min"
    else:
        return f"{seconds}sec"

