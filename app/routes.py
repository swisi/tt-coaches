from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file, abort, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models import User, Certificate, Experience, TrainingPlan, TrainingActivity
from app.forms import (ProfileForm, CertificateForm, ExperienceForm, TrainingPlanForm, 
                      TrainingActivityForm, AdminUserForm)
from app.utils import save_certificate_file, calculate_activity_times, get_next_start_time, check_activity_status
from app.backup_restore import export_backup, import_backup, create_backup_zip, restore_backup_from_zip
from datetime import datetime, date, time, timedelta
import csv
import io
import os

bp = Blueprint('routes', __name__)

def admin_required(f):
    """Decorator für Admin-only Routen"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def check_profile_complete():
    """Prüft ob das Profil vollständig ist und leitet bei Bedarf um"""
    if current_user.is_authenticated and not current_user.is_profile_complete():
        if request.endpoint not in ['routes.profile', 'auth.logout']:
            flash('Bitte vervollständige zuerst dein Profil.', 'warning')
            return redirect(url_for('routes.profile'))
    return None

@bp.before_request
def before_request():
    """Prüft Profilvollständigkeit vor jeder Anfrage"""
    if current_user.is_authenticated:
        check_profile_complete()

# Dashboard
@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    # Heutiger Trainingsplan
    today = datetime.now().date()
    weekday = today.weekday()
    today_plan = TrainingPlan.query.filter(
        TrainingPlan.start_date <= today,
        TrainingPlan.end_date >= today,
        TrainingPlan.weekday == weekday
    )
    
    if not current_user.is_admin:
        today_plan = today_plan.filter(TrainingPlan.team_name == current_user.team)
    
    today_plan = today_plan.first()
    
    # Statistiken
    cert_count = current_user.certificates.count()
    experience_years = current_user.get_total_experience_years()
    
    # Neueste Zertifikate
    recent_certificates = current_user.certificates.order_by(Certificate.acquisition_date.desc()).limit(5).all()
    
    # Neueste Erfahrungen
    recent_experiences = current_user.experiences.order_by(Experience.start_year.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                        today_plan=today_plan,
                        cert_count=cert_count,
                        experience_years=experience_years,
                        recent_certificates=recent_certificates,
                        recent_experiences=recent_experiences)

# Profil
@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        try:
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.full_name = f"{form.first_name.data} {form.last_name.data}"
            current_user.birth_date = form.birth_date.data
            current_user.address = form.address.data
            current_user.zip_code = form.zip_code.data
            current_user.city = form.city.data
            current_user.mobile_phone = form.mobile_phone.data
            current_user.team = form.team.data
            current_user.license_number = form.license_number.data or None
            
            if form.new_password.data:
                current_user.set_password(form.new_password.data)
            
            db.session.commit()
            flash('Profil erfolgreich aktualisiert.', 'success')
            return redirect(url_for('routes.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Speichern: {str(e)}', 'error')
    
    return render_template('profile.html', form=form)

# Zertifikate
@bp.route('/certificates')
@login_required
def certificates():
    certs = current_user.certificates.order_by(Certificate.acquisition_date.desc()).all()
    return render_template('certificates.html', certificates=certs)

@bp.route('/certificates/new', methods=['GET', 'POST'])
@login_required
def new_certificate():
    form = CertificateForm()
    
    if form.validate_on_submit():
        cert = Certificate(
            user_id=current_user.id,
            title=form.title.data,
            organization=form.organization.data,
            acquisition_date=form.acquisition_date.data,
            valid_until=form.valid_until.data if form.valid_until.data else None
        )
        
        if form.file.data:
            file_url = save_certificate_file(form.file.data)
            if file_url:
                cert.file_url = file_url
        
        db.session.add(cert)
        db.session.commit()
        flash('Zertifikat erfolgreich hinzugefügt.', 'success')
        return redirect(url_for('routes.certificates'))
    
    return render_template('certificate_form.html', form=form, title='Neues Zertifikat')

@bp.route('/certificates/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_certificate(id):
    cert = Certificate.query.get_or_404(id)
    
    if cert.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    form = CertificateForm(obj=cert)
    
    if form.validate_on_submit():
        cert.title = form.title.data
        cert.organization = form.organization.data
        cert.acquisition_date = form.acquisition_date.data
        cert.valid_until = form.valid_until.data if form.valid_until.data else None
        
        if form.file.data:
            file_url = save_certificate_file(form.file.data)
            if file_url:
                cert.file_url = file_url
        
        db.session.commit()
        flash('Zertifikat erfolgreich aktualisiert.', 'success')
        return redirect(url_for('routes.certificates'))
    
    return render_template('certificate_form.html', form=form, certificate=cert, title='Zertifikat bearbeiten')

@bp.route('/certificates/<int:id>/delete', methods=['POST'])
@login_required
def delete_certificate(id):
    cert = Certificate.query.get_or_404(id)
    
    if cert.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    db.session.delete(cert)
    db.session.commit()
    flash('Zertifikat erfolgreich gelöscht.', 'success')
    return redirect(url_for('routes.certificates'))

# Erfahrung
@bp.route('/experience')
@login_required
def experience():
    experiences = current_user.experiences.order_by(Experience.start_year.desc()).all()
    return render_template('experience.html', experiences=experiences)

@bp.route('/experience/new', methods=['GET', 'POST'])
@login_required
def new_experience():
    form = ExperienceForm()
    
    if form.validate_on_submit():
        exp = Experience(
            user_id=current_user.id,
            start_year=form.start_year.data,
            end_year=form.end_year.data if form.end_year.data else None,
            team=form.team.data,
            position=form.position.data
        )
        db.session.add(exp)
        db.session.commit()
        flash('Erfahrung erfolgreich hinzugefügt.', 'success')
        return redirect(url_for('routes.experience'))
    
    return render_template('experience_form.html', form=form, title='Neue Erfahrung')

@bp.route('/experience/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_experience(id):
    exp = Experience.query.get_or_404(id)
    
    if exp.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    form = ExperienceForm(obj=exp)
    
    if form.validate_on_submit():
        exp.start_year = form.start_year.data
        exp.end_year = form.end_year.data if form.end_year.data else None
        exp.team = form.team.data
        exp.position = form.position.data
        db.session.commit()
        flash('Erfahrung erfolgreich aktualisiert.', 'success')
        return redirect(url_for('routes.experience'))
    
    return render_template('experience_form.html', form=form, experience=exp, title='Erfahrung bearbeiten')

@bp.route('/experience/<int:id>/delete', methods=['POST'])
@login_required
def delete_experience(id):
    exp = Experience.query.get_or_404(id)
    
    if exp.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    db.session.delete(exp)
    db.session.commit()
    flash('Erfahrung erfolgreich gelöscht.', 'success')
    return redirect(url_for('routes.experience'))

# Coaches-Übersicht
@bp.route('/coaches')
@login_required
def coaches():
    search = request.args.get('search', '')
    coaches_list = User.query.filter(User.is_admin == False)
    
    if search:
        coaches_list = coaches_list.filter(
            db.or_(
                User.full_name.contains(search),
                User.email.contains(search),
                User.team.contains(search)
            )
        )
    
    coaches_list = coaches_list.order_by(User.full_name).all()
    
    return render_template('coaches.html', coaches=coaches_list, search=search)

# Trainingspläne
@bp.route('/training-plans')
@login_required
def training_plans():
    plans = TrainingPlan.query
    
    if not current_user.is_admin:
        plans = plans.filter(TrainingPlan.team_name == current_user.team)
    
    plans = plans.order_by(TrainingPlan.weekday, TrainingPlan.start_time).all()
    
    return render_template('training_plans.html', plans=plans)

@bp.route('/training-plans/<int:id>')
@login_required
def training_plan_detail(id):
    plan = TrainingPlan.query.get_or_404(id)
    
    if not current_user.is_admin and plan.team_name != current_user.team:
        abort(403)
    
    activities = plan.activities.all()
    
    return render_template('training_plan_detail.html', plan=plan, activities=activities)

@bp.route('/training-plans/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_training_plan():
    form = TrainingPlanForm()
    
    if form.validate_on_submit():
        plan = TrainingPlan(
            title=form.title.data,
            team_name=form.team_name.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            weekday=form.weekday.data,
            start_time=form.start_time.data,
            dresscode=form.dresscode.data or None,
            focus=form.focus.data or None,
            goals=form.goals.data or None
        )
        db.session.add(plan)
        db.session.commit()
        flash('Trainingsplan erfolgreich erstellt.', 'success')
        return redirect(url_for('routes.training_plan_detail', id=plan.id))
    
    return render_template('training_plan_form.html', form=form, title='Neuer Trainingsplan')

@bp.route('/training-plans/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_training_plan(id):
    plan = TrainingPlan.query.get_or_404(id)
    form = TrainingPlanForm(obj=plan)
    
    if form.validate_on_submit():
        plan.title = form.title.data
        plan.team_name = form.team_name.data
        plan.start_date = form.start_date.data
        plan.end_date = form.end_date.data
        plan.weekday = form.weekday.data
        plan.start_time = form.start_time.data
        plan.dresscode = form.dresscode.data or None
        plan.focus = form.focus.data or None
        plan.goals = form.goals.data or None
        db.session.commit()
        flash('Trainingsplan erfolgreich aktualisiert.', 'success')
        return redirect(url_for('routes.training_plan_detail', id=plan.id))
    
    return render_template('training_plan_form.html', form=form, plan=plan, title='Trainingsplan bearbeiten')

@bp.route('/training-plans/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_training_plan(id):
    plan = TrainingPlan.query.get_or_404(id)
    db.session.delete(plan)
    db.session.commit()
    flash('Trainingsplan erfolgreich gelöscht.', 'success')
    return redirect(url_for('routes.training_plans'))

@bp.route('/training-plans/<int:id>/copy', methods=['GET', 'POST'])
@login_required
@admin_required
def copy_training_plan(id):
    original_plan = TrainingPlan.query.get_or_404(id)
    form = TrainingPlanForm()
    
    if request.method == 'POST' and form.validate():
        # Neuen Plan erstellen
        new_plan = TrainingPlan(
            title=form.title.data or f"{original_plan.title} (Kopie)",
            team_name=form.team_name.data or original_plan.team_name,
            start_date=form.start_date.data or original_plan.start_date,
            end_date=form.end_date.data or original_plan.end_date,
            weekday=form.weekday.data,
            start_time=form.start_time.data or original_plan.start_time,
            dresscode=original_plan.dresscode,
            focus=original_plan.focus,
            goals=original_plan.goals
        )
        db.session.add(new_plan)
        db.session.flush()  # Um die ID zu erhalten
        
        # Aktivitäten kopieren
        for activity in original_plan.activities.all():
            new_activity = TrainingActivity(
                plan_id=new_plan.id,
                activity_name=activity.activity_name,
                activity_type=activity.activity_type,
                duration_minutes=activity.duration_minutes,
                groups=activity.groups.copy() if activity.groups else None,
                notes=activity.notes,
                order=activity.order
            )
            db.session.add(new_activity)
        
        # Zeiten neu berechnen
        new_plan.activities = TrainingActivity.query.filter_by(plan_id=new_plan.id).all()
        calculate_activity_times(new_plan, new_plan.activities)
        
        db.session.commit()
        flash('Trainingsplan erfolgreich kopiert.', 'success')
        return redirect(url_for('routes.training_plan_detail', id=new_plan.id))
    
    # Formular mit Original-Daten vorausfüllen
    form.team_name.data = original_plan.team_name
    form.start_date.data = original_plan.start_date
    form.end_date.data = original_plan.end_date
    form.start_time.data = original_plan.start_time
    
    return render_template('training_plan_form.html', form=form, title='Trainingsplan kopieren', copy=True)

# Aktivitäten
@bp.route('/training-plans/<int:plan_id>/activities/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_activity(plan_id):
    plan = TrainingPlan.query.get_or_404(plan_id)
    form = TrainingActivityForm()
    # Setze Standard-Wert auf 'team_wide'
    form.activity_type.data = 'team_wide'
    
    if form.validate_on_submit():
        # Nächste Order-Nummer finden
        max_order = db.session.query(func.max(TrainingActivity.order)).filter_by(plan_id=plan_id).scalar() or 0
        
        # Sammle group_activities für group_specific, special_teams und position_specific
        group_activities = {}
        if form.activity_type.data == 'group_specific' or form.activity_type.data == 'special_teams':
            for key, value in request.form.items():
                if key.startswith('group_activity_'):
                    combination_key = key.replace('group_activity_', '')
                    if value and value.strip():
                        # Sortiere die Gruppen im Key, damit Keys konsistent sind
                        groups = sorted([g.strip() for g in combination_key.split(',')])
                        sorted_key = ','.join(groups)
                        group_activities[sorted_key] = value.strip()
        elif form.activity_type.data == 'position_specific':
            for key, value in request.form.items():
                if key.startswith('position_activity_'):
                    group = key.replace('position_activity_', '')
                    if value and value.strip():
                        group_activities[group] = value.strip()
        
        activity = TrainingActivity(
            plan_id=plan_id,
            activity_name=form.activity_name.data,
            activity_type=form.activity_type.data,
            duration_minutes=form.duration_minutes.data,
            groups=form.get_groups_dict(),
            group_activities=group_activities if group_activities else None,
            notes=form.notes.data or None,
            order=max_order + 1
        )
        
        # Zeiten berechnen
        activities = plan.activities
        calculate_activity_times(plan, activities, activity)
        
        db.session.add(activity)
        db.session.commit()
        flash('Aktivität erfolgreich hinzugefügt.', 'success')
        return redirect(url_for('routes.training_plan_detail', id=plan_id))
    
    return render_template('activity_form.html', form=form, plan=plan, title='Neue Aktivität')

@bp.route('/training-plans/<int:plan_id>/activities/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_activity(plan_id, id):
    plan = TrainingPlan.query.get_or_404(plan_id)
    activity = TrainingActivity.query.get_or_404(id)
    
    if activity.plan_id != plan_id:
        abort(404)
    
    form = TrainingActivityForm(obj=activity)
    
    # Gruppen-Checkboxes vorausfüllen
    if activity.groups:
        for group, active in activity.groups.items():
            field_name = f'group_{group}'
            if hasattr(form, field_name):
                getattr(form, field_name).data = active
    
    if form.validate_on_submit():
        activity.activity_name = form.activity_name.data
        activity.activity_type = form.activity_type.data
        activity.duration_minutes = form.duration_minutes.data
        activity.groups = form.get_groups_dict()
        
        # Sammle group_activities für group_specific, special_teams und position_specific
        if form.activity_type.data == 'group_specific' or form.activity_type.data == 'special_teams':
            group_activities = {}
            for key, value in request.form.items():
                if key.startswith('group_activity_'):
                    combination_key = key.replace('group_activity_', '')
                    if value and value.strip():
                        # Sortiere die Gruppen im Key, damit Keys konsistent sind
                        groups = sorted([g.strip() for g in combination_key.split(',')])
                        sorted_key = ','.join(groups)
                        group_activities[sorted_key] = value.strip()
            activity.group_activities = group_activities if group_activities else None
        elif form.activity_type.data == 'position_specific':
            group_activities = {}
            for key, value in request.form.items():
                if key.startswith('position_activity_'):
                    group = key.replace('position_activity_', '')
                    if value and value.strip():
                        group_activities[group] = value.strip()
            activity.group_activities = group_activities if group_activities else None
        else:
            activity.group_activities = None
        
        activity.notes = form.notes.data or None
        
        # Zeiten neu berechnen
        calculate_activity_times(plan, plan.activities)
        
        db.session.commit()
        flash('Aktivität erfolgreich aktualisiert.', 'success')
        return redirect(url_for('routes.training_plan_detail', id=plan_id))
    
    return render_template('activity_form.html', form=form, plan=plan, activity=activity, title='Aktivität bearbeiten')

@bp.route('/training-plans/<int:plan_id>/activities/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_activity(plan_id, id):
    activity = TrainingActivity.query.get_or_404(id)
    
    if activity.plan_id != plan_id:
        abort(404)
    
    db.session.delete(activity)
    
    # Zeiten neu berechnen
    plan = TrainingPlan.query.get_or_404(plan_id)
    calculate_activity_times(plan, plan.activities)
    
    db.session.commit()
    flash('Aktivität erfolgreich gelöscht.', 'success')
    return redirect(url_for('routes.training_plan_detail', id=plan_id))

@bp.route('/training-plans/<int:plan_id>/activities/reorder', methods=['POST'])
@login_required
@admin_required
def reorder_activities(plan_id):
    plan = TrainingPlan.query.get_or_404(plan_id)
    data = request.get_json()
    
    if 'order' not in data:
        return jsonify({'error': 'Keine Reihenfolge angegeben'}), 400
    
    # Aktualisiere Order-Werte
    for activity_id, order in data['order'].items():
        activity = TrainingActivity.query.get(activity_id)
        if activity and activity.plan_id == plan_id:
            activity.order = order
    
    # Zeiten neu berechnen
    calculate_activity_times(plan, plan.activities)
    
    db.session.commit()
    return jsonify({'success': True})

# Live-Tracking API
@bp.route('/api/training-plans/<int:id>/activities/status')
@login_required
def get_activity_status(id):
    plan = TrainingPlan.query.get_or_404(id)
    
    if not current_user.is_admin and plan.team_name != current_user.team:
        abort(403)
    
    activities = plan.activities.all()
    status = {}
    
    for activity in activities:
        activity_status = check_activity_status(activity, plan)
        if activity_status:
            status[activity.id] = activity_status
    
    return jsonify(status)

# Admin-Bereich
@bp.route('/admin/coaches')
@login_required
@admin_required
def admin_coaches():
    search = request.args.get('search', '')
    coaches_list = User.query
    
    if search:
        coaches_list = coaches_list.filter(
            db.or_(
                User.full_name.contains(search),
                User.email.contains(search)
            )
        )
    
    coaches_list = coaches_list.order_by(User.full_name).all()
    
    return render_template('admin/coaches.html', coaches=coaches_list, search=search)

@bp.route('/admin/coaches/export')
@login_required
@admin_required
def export_coaches_csv():
    coaches = User.query.order_by(User.full_name).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Vollständiger Name', 'E-Mail', 'Team', 'Mobiltelefon', 'Lizenznummer',
        'Straße', 'PLZ', 'Ort', 'Geburtsdatum', 'Anzahl Zertifikate', 'Jahre Erfahrung'
    ])
    
    # Daten
    for coach in coaches:
        writer.writerow([
            coach.full_name or '',
            coach.email,
            coach.team or '',
            coach.mobile_phone or '',
            coach.license_number or '',
            coach.address or '',
            coach.zip_code or '',
            coach.city or '',
            coach.birth_date.strftime('%d.%m.%Y') if coach.birth_date else '',
            coach.certificates.count(),
            coach.get_total_experience_years()
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'coaches_export_{datetime.now().strftime("%Y%m%d")}.csv'
    )

@bp.route('/admin/coaches/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_coach(id):
    coach = User.query.get_or_404(id)
    form = AdminUserForm(obj=coach)
    
    if form.validate_on_submit():
        coach.email = form.email.data
        coach.first_name = form.first_name.data
        coach.last_name = form.last_name.data
        coach.full_name = f"{form.first_name.data} {form.last_name.data}"
        coach.birth_date = form.birth_date.data
        coach.address = form.address.data
        coach.zip_code = form.zip_code.data
        coach.city = form.city.data
        coach.mobile_phone = form.mobile_phone.data
        coach.team = form.team.data
        coach.license_number = form.license_number.data or None
        coach.is_admin = form.is_admin.data
        
        if form.new_password.data:
            coach.set_password(form.new_password.data)
        
        db.session.commit()
        flash('Coach erfolgreich aktualisiert.', 'success')
        return redirect(url_for('routes.admin_coaches'))
    
    certificates = coach.certificates.all()
    return render_template('admin/coach_detail.html', coach=coach, form=form, certificates=certificates)

# Backup & Restore
@bp.route('/admin/backup')
@login_required
@admin_required
def backup_data():
    """Erstellt ein Backup aller Daten (inklusive Dateien)"""
    try:
        zip_buffer = create_backup_zip()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'coaches_backup_{timestamp}.zip'
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Fehler beim Erstellen des Backups: {str(e)}', 'error')
        return redirect(url_for('routes.admin_backup_restore'))

@bp.route('/admin/restore', methods=['GET', 'POST'])
@login_required
@admin_required
def restore_data():
    """Stellt Daten aus einem Backup wieder her"""
    if request.method == 'POST':
        if 'backup_file' not in request.files:
            flash('Keine Datei ausgewählt.', 'error')
            return redirect(url_for('routes.admin_backup_restore'))
        
        file = request.files['backup_file']
        if file.filename == '':
            flash('Keine Datei ausgewählt.', 'error')
            return redirect(url_for('routes.admin_backup_restore'))
        
        # Unterstütze sowohl ZIP als auch JSON (für Rückwärtskompatibilität)
        is_zip = file.filename.endswith('.zip')
        is_json = file.filename.endswith('.json')
        
        if not (is_zip or is_json):
            flash('Nur ZIP- oder JSON-Dateien werden unterstützt.', 'error')
            return redirect(url_for('routes.admin_backup_restore'))
        
        try:
            clear_existing = request.form.get('clear_existing') == 'on'
            
            # Speichere den aktuell eingeloggten Benutzer, falls clear_existing aktiviert ist
            current_user_email = None
            current_user_is_admin = False
            if clear_existing and current_user.is_authenticated:
                current_user_email = current_user.email
                current_user_is_admin = current_user.is_admin
            
            if is_zip:
                # ZIP-Backup (mit Dateien)
                success, message, stats = restore_backup_from_zip(file, clear_existing=clear_existing)
            else:
                # JSON-Backup (nur Daten, Rückwärtskompatibilität)
                backup_json = file.read().decode('utf-8')
                success, message, stats = import_backup(backup_json, clear_existing=clear_existing)
            
            # Nach dem Restore: Prüfe ob der eingeloggte Benutzer noch existiert
            if success and clear_existing and current_user_email:
                from flask_login import logout_user
                restored_user = User.query.filter_by(email=current_user_email).first()
                if restored_user:
                    # Benutzer wurde wiederhergestellt, Session bleibt aktiv
                    pass
                else:
                    # Benutzer wurde nicht wiederhergestellt, logge aus
                    logout_user()
                    flash('Restore abgeschlossen. Bitte melde dich erneut an.', 'info')
                    return redirect(url_for('auth.login'))
            
            # Nach dem Restore: Prüfe ob der eingeloggte Benutzer noch existiert
            if success and clear_existing:
                # Lade den Benutzer neu aus der Datenbank
                from flask_login import logout_user
                db.session.expire_all()  # Erzwinge Neuladen aus DB
                try:
                    # Prüfe ob current_user noch in der DB existiert
                    user = User.query.get(current_user.id)
                    if not user:
                        # Benutzer wurde gelöscht, logge aus
                        logout_user()
                        flash('Restore abgeschlossen. Bitte melde dich mit einem Benutzer aus dem Backup erneut an.', 'info')
                        return redirect(url_for('auth.login'))
                except Exception:
                    # Fehler beim Zugriff auf current_user, logge aus
                    logout_user()
                    flash('Restore abgeschlossen. Bitte melde dich erneut an.', 'info')
                    return redirect(url_for('auth.login'))
            
            if success:
                flash(message, 'success')
            else:
                flash(message, 'error')
        except Exception as e:
            flash(f'Fehler beim Wiederherstellen: {str(e)}', 'error')
        
        return redirect(url_for('routes.admin_backup_restore'))
    
    return redirect(url_for('routes.admin_backup_restore'))

@bp.route('/admin/backup-restore')
@login_required
@admin_required
def admin_backup_restore():
    """Backup & Restore Verwaltungsseite"""
    return render_template('admin/backup_restore.html')

# Route zum Servieren von Upload-Dateien (falls Flask sie nicht automatisch findet)
@bp.route('/static/uploads/certificates/<path:filename>')
@login_required
def serve_certificate_file(filename):
    """Serviert Zertifikatsdateien explizit"""
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, filename)
        
        # Sicherheitsprüfung: Stelle sicher, dass die Datei im Upload-Ordner ist
        if not os.path.abspath(file_path).startswith(os.path.abspath(upload_folder)):
            abort(403)
        
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            abort(404)
    except Exception as e:
        current_app.logger.error(f"Fehler beim Servieren der Datei {filename}: {str(e)}")
        abort(404)

