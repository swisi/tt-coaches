"""
Datenbank-Modelle für die Anwendung
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc
from app import db

class User(UserMixin, db.Model):
    """Benutzer-Modell"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Rollen-Flags für schnelle und stabile Prüfungen
    is_superadmin = db.Column('is_superadmin', db.Boolean, default=False, nullable=False, index=True)
    is_admin = db.Column('is_admin', db.Boolean, default=False, nullable=False, index=True)
    is_coach = db.Column('is_coach', db.Boolean, default=False, nullable=False, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehung zum Trainer-Profil
    trainer_profile = db.relationship('TrainerProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Passwort setzen"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Passwort prüfen"""
        return check_password_hash(self.password_hash, password)
    
    
    def get_role_name(self):
        """Gibt den Rollennamen zurück (für Anzeige) - zeigt die höchste aktive Rolle"""
        # Verwende direkte DB-Abfrage für korrekte Werte
        from sqlalchemy import text
        from app import db
        if hasattr(self, 'id') and self.id:
            try:
                result = db.session.execute(
                    text("SELECT is_superadmin, is_admin, is_coach FROM users WHERE id = :user_id"),
                    {"user_id": self.id}
                ).first()
                if result:
                    if result[0]:  # is_superadmin
                        return 'superadmin'
                    elif result[1]:  # is_admin
                        return 'admin'
                    elif result[2]:  # is_coach
                        return 'coach'
            except Exception:
                pass
        return 'unbekannt'
    
    def get_active_roles(self):
        """Gibt eine Liste aller aktiven Rollen zurück"""
        roles = []
        # Verwende direkte DB-Abfrage für korrekte Werte
        from sqlalchemy import text
        from app import db
        if hasattr(self, 'id') and self.id:
            try:
                result = db.session.execute(
                    text("SELECT is_superadmin, is_admin, is_coach FROM users WHERE id = :user_id"),
                    {"user_id": self.id}
                ).first()
                if result:
                    if result[0]:  # is_superadmin
                        roles.append('Superadministrator')
                    if result[1]:  # is_admin
                        roles.append('Administrator')
                    if result[2]:  # is_coach
                        roles.append('Coach')
            except Exception:
                pass
        return roles if roles else ['Keine Rolle']
    
    def is_superadmin(self):
        """Prüft ob Benutzer Superadministrator ist - direkt über Flag (stabil und schnell)"""
        # SQLAlchemy speichert Spaltenwerte in verschiedenen Orten
        # Versuche zuerst über getattr direkt (SQLAlchemy Descriptor)
        try:
            # Versuche direkten Zugriff über getattr (umgeht Methode)
            value = getattr(type(self), 'is_superadmin').__get__(self, type(self))
            # Wenn es ein Column-Descriptor ist, sollte es den Wert zurückgeben
            # Aber wenn es None ist, prüfe direkt in der DB
            if value is not None:
                return bool(value)
        except (AttributeError, TypeError):
            pass
        
        # Fallback: Direkte Abfrage aus der Datenbank wenn Instanz-ID vorhanden
        if hasattr(self, 'id') and self.id:
            from sqlalchemy import text
            from app import db
            try:
                result = db.session.execute(
                    text("SELECT is_superadmin FROM users WHERE id = :user_id"),
                    {"user_id": self.id}
                ).scalar()
                if result is not None:
                    return bool(result)
            except Exception:
                pass
        
        return False
    
    def is_admin(self):
        """Prüft ob Benutzer Administrator ist - direkt über Flag (stabil und schnell)"""
        try:
            value = getattr(type(self), 'is_admin').__get__(self, type(self))
            if value is not None:
                return bool(value)
        except (AttributeError, TypeError):
            pass
        
        if hasattr(self, 'id') and self.id:
            from sqlalchemy import text
            from app import db
            try:
                result = db.session.execute(
                    text("SELECT is_admin FROM users WHERE id = :user_id"),
                    {"user_id": self.id}
                ).scalar()
                if result is not None:
                    return bool(result)
            except Exception:
                pass
        
        return False
    
    def is_coach(self):
        """Prüft ob Benutzer Coach ist - direkt über Flag (stabil und schnell)"""
        try:
            value = getattr(type(self), 'is_coach').__get__(self, type(self))
            if value is not None:
                return bool(value)
        except (AttributeError, TypeError):
            pass
        
        if hasattr(self, 'id') and self.id:
            from sqlalchemy import text
            from app import db
            try:
                result = db.session.execute(
                    text("SELECT is_coach FROM users WHERE id = :user_id"),
                    {"user_id": self.id}
                ).scalar()
                if result is not None:
                    return bool(result)
            except Exception:
                pass
        
        return False
    
    def can_manage_users(self):
        """Prüft ob Benutzer andere Benutzer verwalten kann - nur Superadministratoren"""
        return self.is_superadmin()
    
    def can_manage_trainers(self):
        """Prüft ob Benutzer Trainer verwalten kann - Administratoren und Superadministratoren"""
        return self.is_superadmin() or self.is_admin()
    
    def __repr__(self):
        return f'<User {self.username}>'

class TrainerProfile(db.Model):
    """Trainer-Profil-Modell"""
    __tablename__ = 'trainer_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Persönliche Daten
    license_number = db.Column(db.String(50))  # Lizenznummer
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    profile_image_path = db.Column(db.String(500))  # Pfad zum Profilbild
    street = db.Column(db.String(200))
    postal_code = db.Column(db.String(10))
    city = db.Column(db.String(100))
    phone_private = db.Column(db.String(20))
    phone_business = db.Column(db.String(20))
    email_private = db.Column(db.String(120))
    email_business = db.Column(db.String(120))
    function_club = db.Column(db.String(200))  # Funktion im Club
    
    # Curriculum Vitae
    cv_text = db.Column(db.Text)  # Strukturierter Text-CV
    cv_file_path = db.Column(db.String(500))  # Pfad zur hochgeladenen CV-Datei
    
    # Status
    active = db.Column(db.Boolean, default=True, nullable=False)  # Trainer aktiv/inaktiv
    
    # Zeitstempel
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    certificates = db.relationship('Certificate', backref='trainer_profile', lazy='dynamic', cascade='all, delete-orphan')
    coaching_experiences = db.relationship('CoachingExperience', backref='trainer_profile', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_email_private(self):
        """Gibt E-Mail privat zurück, falls vorhanden, sonst die User-E-Mail"""
        return self.email_private or (self.user.email if self.user else None)
    
    def get_total_coaching_years(self):
        """Berechnet die Gesamtanzahl der Jahre an Coaching-Erfahrung"""
        from datetime import datetime
        current_year = datetime.now().year
        total_years = 0
        
        for exp in self.coaching_experiences:
            if exp.end_year:
                # Erfahrung mit Endjahr: end_year - start_year + 1
                years = exp.end_year - exp.start_year + 1
            else:
                # Laufende Erfahrung: aktuelles Jahr - start_year + 1
                years = current_year - exp.start_year + 1
            
            total_years += years
        
        return total_years
    
    def __repr__(self):
        return f'<TrainerProfile {self.first_name} {self.last_name}>'

class CoachingExperience(db.Model):
    """Coaching-Erfahrung Modell"""
    __tablename__ = 'coaching_experiences'
    
    # Coaching-Rollen
    ROLES = [
        ('Assistant Coach', 'Assistant Coach'),
        ('Position Coach', 'Position Coach'),
        ('Offense Coordinator', 'Offense Coordinator'),
        ('Defense Coordinator', 'Defense Coordinator'),
        ('Head Coach', 'Head Coach')
    ]
    
    # Teams
    TEAMS = [
        ('U8', 'U8'),
        ('U13', 'U13'),
        ('U16 Flag', 'U16 Flag'),
        ('U16 Tackle', 'U16 Tackle'),
        ('U19 Tackle', 'U19 Tackle'),
        ('1ste Mannschaft', '1ste Mannschaft'),
        ('Ultimate Flag', 'Ultimate Flag')
    ]
    
    # Positionen
    POSITIONS = [
        ('', ''),  # Leerer Wert für "Keine Auswahl"
        ('Offense', 'Offense'),
        ('Defense', 'Defense'),
        ('Special Team', 'Special Team'),
        ('Quarter Backs', 'Quarter Backs'),
        ('Running Backs', 'Running Backs'),
        ('Receiver', 'Receiver'),
        ('Lineman', 'Lineman'),
        ('Linebacker', 'Linebacker'),
        ('Defensive Back', 'Defensive Back')
    ]
    
    id = db.Column(db.Integer, primary_key=True)
    trainer_profile_id = db.Column(db.Integer, db.ForeignKey('trainer_profiles.id'), nullable=False)
    
    start_year = db.Column(db.Integer, nullable=False)
    end_year = db.Column(db.Integer, nullable=True)  # Optional für laufende Erfahrungen
    coaching_role = db.Column(db.String(50), nullable=False)  # Eine der ROLES
    team = db.Column(db.String(50), nullable=False)  # Eines der TEAMS
    position = db.Column(db.String(50), nullable=True)  # Eine der POSITIONS (optional)
    
    # Zeitstempel
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        end_str = f"-{self.end_year}" if self.end_year else "-laufend"
        return f'<CoachingExperience {self.start_year}{end_str} {self.coaching_role} {self.team}>'

class Certificate(db.Model):
    """Zertifikat-Modell"""
    __tablename__ = 'certificates'
    
    # Ausbildungsarten
    TRAINING_TYPES = [
        ('', 'leer'),
        ('Zertifikat', 'Zertifikat'),
        ('Convention', 'Convention'),
        ('Other', 'Other')
    ]
    
    id = db.Column(db.Integer, primary_key=True)
    trainer_profile_id = db.Column(db.Integer, db.ForeignKey('trainer_profiles.id'), nullable=False)
    
    # Zertifikat-Daten
    title = db.Column(db.String(200), nullable=False)
    issuer = db.Column(db.String(200))  # Ausstellende Organisation
    issue_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)  # Optional, falls ablaufend
    description = db.Column(db.Text)
    training_type = db.Column(db.String(50))  # Ausbildungsart: Zertifikat, Convention, leer, Other
    
    # Datei-Upload
    file_path = db.Column(db.String(500), nullable=True)  # Pfad zur hochgeladenen Datei (optional)
    file_type = db.Column(db.String(10))  # pdf, png, jpg, etc.
    
    # Zeitstempel
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Certificate {self.title}>'

