"""
Coach-Blueprint (für Trainer)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory
from flask_login import login_required, current_user
from app import db
from app.models import TrainerProfile, Certificate, CoachingExperience
from app.forms import TrainerProfileForm, CertificateForm, CoachingExperienceForm
from app.utils import save_uploaded_file, delete_file
from config import Config
from pathlib import Path
from flask_wtf.file import FileAllowed
from wtforms.validators import Optional

bp = Blueprint('coach', __name__)

def require_coach():
    """Prüft ob Benutzer ein Coach ist"""
    if not current_user.is_coach():
        flash('Zugriff verweigert. Diese Seite ist nur für Trainer verfügbar.', 'error')
        return redirect(url_for('main.dashboard'))
    return None

@bp.route('/')
@login_required
def overview():
    """Coach-Übersichtsseite"""
    result = require_coach()
    if result:
        return result
    
    profile = current_user.trainer_profile
    
    if profile is None:
        # Erstelle neues Profil falls noch nicht vorhanden
        profile = TrainerProfile(
            user_id=current_user.id,
            first_name='',
            last_name=''
        )
        db.session.add(profile)
        db.session.commit()
        flash('Bitte vervollständigen Sie Ihr Profil.', 'info')
        return redirect(url_for('coach.profile'))
    
    # Statistik-Daten
    certificates_count = profile.certificates.count()
    certificates = profile.certificates.order_by(Certificate.issue_date.desc()).limit(5).all()
    coaching_experiences_count = profile.coaching_experiences.count()
    
    # E-Mail privat vom User übernehmen falls nicht im Profil gesetzt
    if not profile.email_private and current_user.email:
        profile.email_private = current_user.email
        db.session.commit()
    
    return render_template('coach/overview.html', 
                         profile=profile, 
                         certificates=certificates, 
                         certificates_count=certificates_count,
                         coaching_experiences_count=coaching_experiences_count)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Trainer-Profil anzeigen und bearbeiten"""
    result = require_coach()
    if result:
        return result
    
    profile = current_user.trainer_profile
    
    if profile is None:
        # Erstelle neues Profil falls noch nicht vorhanden
        profile = TrainerProfile(user_id=current_user.id, first_name='', last_name='')
        db.session.add(profile)
        db.session.commit()
    
    # E-Mail privat vom User übernehmen falls nicht im Profil gesetzt
    if not profile.email_private and current_user.email:
        profile.email_private = current_user.email
        db.session.commit()
    
    form = TrainerProfileForm(obj=profile)
    
    # Setze Standard-E-Mail vom User wenn noch nicht gesetzt
    if not form.email_private.data and current_user.email:
        form.email_private.data = current_user.email
    
    if form.validate_on_submit():
        # Aktualisiere Profildaten (ohne Profilbild, das wird separat behandelt)
        # Speichere Profilbild-Feld temporär
        profile_image_data = form.profile_image.data
        form.profile_image.data = None  # Setze auf None, damit es nicht gespeichert wird
        form.populate_obj(profile)
        form.profile_image.data = profile_image_data  # Stelle wieder her
        
        db.session.commit()
        flash('Ihr Profil wurde erfolgreich aktualisiert.', 'success')
        return redirect(url_for('coach.profile'))
    
    # Lade Coaching-Erfahrungen (absteigend sortiert, laufende zuerst)
    from sqlalchemy import case, desc
    coaching_experiences = profile.coaching_experiences.order_by(
        case((CoachingExperience.end_year.is_(None), 0), else_=1),  # Laufende (NULL) zuerst
        desc(CoachingExperience.end_year),
        desc(CoachingExperience.start_year)
    ).all()
    
    # Lade Zertifikate (absteigend sortiert nach Ausstellungsdatum)
    certificates = profile.certificates.order_by(
        desc(Certificate.issue_date),
        desc(Certificate.created_at)
    ).all()
    
    return render_template('coach/profile.html', form=form, profile=profile, coaching_experiences=coaching_experiences, certificates=certificates)

@bp.route('/certificates')
@login_required
def certificates():
    """Zertifikate-Übersicht"""
    result = require_coach()
    if result:
        return result
    
    profile = current_user.trainer_profile
    if profile is None:
        return redirect(url_for('coach.profile'))
    
    certificates_list = profile.certificates.order_by(Certificate.issue_date.desc()).all()
    return render_template('coach/certificates.html', certificates=certificates_list)

@bp.route('/certificates/add', methods=['GET', 'POST'])
@login_required
def add_certificate():
    """Neues Zertifikat hinzufügen"""
    result = require_coach()
    if result:
        return result
    
    profile = current_user.trainer_profile
    if profile is None:
        flash('Bitte vervollständigen Sie zuerst Ihr Profil.', 'warning')
        return redirect(url_for('coach.profile'))
    
    form = CertificateForm()
    
    if form.validate_on_submit():
        # Speichere hochgeladene Datei
        file_path = save_uploaded_file(
            form.file.data,
            'CERTIFICATES',
            prefix=f'cert_{current_user.id}'
        )
        
        if file_path:
            certificate = Certificate(
                trainer_profile_id=profile.id,
                title=form.title.data,
                issuer=form.issuer.data,
                issue_date=form.issue_date.data,
                expiry_date=form.expiry_date.data,
                description=form.description.data,
                file_path=file_path,
                file_type=form.file.data.filename.rsplit('.', 1)[1].lower()
            )
            db.session.add(certificate)
            db.session.commit()
            flash('Zertifikat wurde erfolgreich hinzugefügt.', 'success')
            return redirect(url_for('coach.profile'))
        else:
            flash('Fehler beim Hochladen der Datei.', 'error')
    
    return render_template('coach/add_certificate.html', form=form)

@bp.route('/certificates/<int:cert_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_certificate(cert_id):
    """Zertifikat bearbeiten"""
    result = require_coach()
    if result:
        return result
    
    profile = current_user.trainer_profile
    if profile is None:
        return redirect(url_for('coach.profile'))
    
    certificate = Certificate.query.get_or_404(cert_id)
    
    # Prüfe ob Zertifikat zum aktuellen Benutzer gehört
    if certificate.trainer_profile_id != profile.id:
        flash('Zugriff verweigert.', 'error')
        return redirect(url_for('coach.profile'))
    
    form = CertificateForm(obj=certificate)
    
    # Datei-Feld optional machen für Edit
    form.file.validators = [Optional(), FileAllowed(['pdf', 'png', 'jpg', 'jpeg', 'gif'], 'Nur PDF und Bilddateien erlaubt')]
    
    if form.validate_on_submit():
        # Wenn eine neue Datei hochgeladen wurde
        if form.file.data:
            # Lösche alte Datei
            delete_file(certificate.file_path)
            
            # Speichere neue Datei
            file_path = save_uploaded_file(
                form.file.data,
                'CERTIFICATES',
                prefix=f'cert_{current_user.id}'
            )
            if file_path:
                certificate.file_path = file_path
                certificate.file_type = form.file.data.filename.rsplit('.', 1)[1].lower()
        
        # Aktualisiere andere Felder (ohne file)
        certificate.title = form.title.data
        certificate.issuer = form.issuer.data
        certificate.issue_date = form.issue_date.data
        certificate.expiry_date = form.expiry_date.data
        certificate.description = form.description.data
        
        db.session.commit()
        flash('Zertifikat wurde erfolgreich aktualisiert.', 'success')
        return redirect(url_for('coach.profile'))
    
    return render_template('coach/edit_certificate.html', form=form, certificate=certificate)

@bp.route('/certificates/<int:cert_id>/delete', methods=['POST'])
@login_required
def delete_certificate(cert_id):
    """Zertifikat löschen"""
    result = require_coach()
    if result:
        return result
    
    profile = current_user.trainer_profile
    if profile is None:
        return redirect(url_for('coach.profile'))
    
    certificate = Certificate.query.get_or_404(cert_id)
    
    # Prüfe ob Zertifikat zum aktuellen Benutzer gehört
    if certificate.trainer_profile_id != profile.id:
        flash('Zugriff verweigert.', 'error')
        return redirect(url_for('coach.profile'))
    
    # Lösche Datei
    delete_file(certificate.file_path)
    
    # Lösche Zertifikat
    db.session.delete(certificate)
    db.session.commit()
    
    flash('Zertifikat wurde erfolgreich gelöscht.', 'success')
    return redirect(url_for('coach.profile'))

@bp.route('/files/<path:filename>')
@login_required
def serve_file(filename):
    """Serviert hochgeladene Dateien (nur für eigenen Benutzer)"""
    result = require_coach()
    if result:
        return result
    
    # Normalisiere Dateiname (konvertiere Backslashes zu Forward-Slashes)
    filename_normalized = filename.replace('\\', '/')
    
    # Sicherheitsprüfung: Nur eigene Dateien
    profile = current_user.trainer_profile
    if profile:
        # Normalisiere gespeicherte Pfade für Vergleich
        profile_image_path = profile.profile_image_path.replace('\\', '/') if profile.profile_image_path else None
        cv_file_path = profile.cv_file_path.replace('\\', '/') if profile.cv_file_path else None
        
        # Prüfe Profilbild
        if profile_image_path and profile_image_path == filename_normalized:
            file_path = Path(Config.UPLOAD_FOLDER) / filename_normalized
            if file_path.exists():
                upload_folder = Path(Config.UPLOAD_FOLDER)
                return send_from_directory(str(upload_folder), filename_normalized)
        
        # Prüfe CV-Datei
        if cv_file_path and cv_file_path == filename_normalized:
            file_path = Path(Config.UPLOAD_FOLDER) / filename_normalized
            if file_path.exists():
                upload_folder = Path(Config.UPLOAD_FOLDER)
                return send_from_directory(str(upload_folder), filename_normalized)
        
        # Prüfe Zertifikat-Dateien
        for cert in profile.certificates:
            cert_path = cert.file_path.replace('\\', '/') if cert.file_path else None
            if cert_path and cert_path == filename_normalized:
                file_path = Path(Config.UPLOAD_FOLDER) / filename_normalized
                if file_path.exists():
                    upload_folder = Path(Config.UPLOAD_FOLDER)
                    return send_from_directory(str(upload_folder), filename_normalized)
    
    flash('Datei nicht gefunden oder Zugriff verweigert.', 'error')
    return redirect(url_for('coach.profile'))

@bp.route('/profile/upload-image', methods=['POST'])
@login_required
def upload_profile_image():
    """Profilbild-Upload (separater Endpoint)"""
    result = require_coach()
    if result:
        return result
    
    profile = current_user.trainer_profile
    if profile is None:
        flash('Bitte vervollständigen Sie zuerst Ihr Profil.', 'warning')
        return redirect(url_for('coach.profile'))
    
    from app.forms import TrainerProfileForm
    form = TrainerProfileForm()
    
    if form.validate_on_submit() and form.profile_image.data:
        # Lösche altes Profilbild falls vorhanden
        if profile.profile_image_path:
            delete_file(profile.profile_image_path)
        
        image_path = save_uploaded_file(
            form.profile_image.data,
            'PROFILE_IMAGES',
            prefix=f'profile_{current_user.id}'
        )
        if image_path:
            profile.profile_image_path = image_path
            db.session.commit()
            flash('Profilbild wurde erfolgreich hochgeladen.', 'success')
        else:
            flash('Fehler beim Hochladen des Profilbilds.', 'error')
    else:
        flash('Bitte wählen Sie ein Bild aus.', 'error')
    
    return redirect(url_for('coach.profile'))

@bp.route('/cv/add', methods=['GET', 'POST'])
@login_required
def add_coaching_experience():
    """Neue Coaching-Erfahrung hinzufügen"""
    result = require_coach()
    if result:
        return result
    
    profile = current_user.trainer_profile
    if profile is None:
        flash('Bitte vervollständigen Sie zuerst Ihr Profil.', 'warning')
        return redirect(url_for('coach.profile'))
    
    form = CoachingExperienceForm()
    
    if form.validate_on_submit():
        experience = CoachingExperience(
            trainer_profile_id=profile.id,
            start_year=form.start_year.data,
            end_year=form.end_year.data,
            coaching_role=form.coaching_role.data,
            team=form.team.data
        )
        db.session.add(experience)
        db.session.commit()
        flash('Coaching-Erfahrung wurde erfolgreich hinzugefügt.', 'success')
        return redirect(url_for('coach.profile'))
    
    return render_template('coach/add_coaching_experience.html', form=form)

@bp.route('/cv/<int:exp_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_coaching_experience(exp_id):
    """Coaching-Erfahrung bearbeiten"""
    result = require_coach()
    if result:
        return result
    
    profile = current_user.trainer_profile
    if profile is None:
        return redirect(url_for('coach.profile'))
    
    experience = CoachingExperience.query.get_or_404(exp_id)
    
    # Prüfe ob Erfahrung zum aktuellen Benutzer gehört
    if experience.trainer_profile_id != profile.id:
        flash('Zugriff verweigert.', 'error')
        return redirect(url_for('coach.profile'))
    
    form = CoachingExperienceForm(obj=experience)
    
    if form.validate_on_submit():
        form.populate_obj(experience)
        db.session.commit()
        flash('Coaching-Erfahrung wurde erfolgreich aktualisiert.', 'success')
        return redirect(url_for('coach.profile'))
    
    return render_template('coach/edit_coaching_experience.html', form=form, experience=experience)

@bp.route('/cv/<int:exp_id>/delete', methods=['POST'])
@login_required
def delete_coaching_experience(exp_id):
    """Coaching-Erfahrung löschen"""
    result = require_coach()
    if result:
        return result
    
    profile = current_user.trainer_profile
    if profile is None:
        return redirect(url_for('coach.profile'))
    
    experience = CoachingExperience.query.get_or_404(exp_id)
    
    # Prüfe ob Erfahrung zum aktuellen Benutzer gehört
    if experience.trainer_profile_id != profile.id:
        flash('Zugriff verweigert.', 'error')
        return redirect(url_for('coach.profile'))
    
    db.session.delete(experience)
    db.session.commit()
    
    flash('Coaching-Erfahrung wurde erfolgreich gelöscht.', 'success')
    return redirect(url_for('coach.profile'))

