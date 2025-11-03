"""
WTForms für die Anwendung
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, DateField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError, EqualTo, NumberRange
from app.models import User, CoachingExperience

class LoginForm(FlaskForm):
    """Login-Formular"""
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('Angemeldet bleiben')

class RegisterForm(FlaskForm):
    """Registrierungsformular für Coaches"""
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('E-Mail', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Passwort bestätigen', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwörter müssen übereinstimmen')
    ])
    
    def validate_username(self, username):
        """Prüft ob Benutzername bereits existiert"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Dieser Benutzername ist bereits vergeben. Bitte wählen Sie einen anderen.')
    
    def validate_email(self, email):
        """Prüft ob E-Mail bereits existiert"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Diese E-Mail-Adresse wird bereits verwendet. Bitte verwenden Sie eine andere.')

class ChangePasswordForm(FlaskForm):
    """Passwort-Änderungsformular"""
    new_password = PasswordField('Neues Passwort', validators=[DataRequired(), Length(min=6)])
    new_password2 = PasswordField('Neues Passwort bestätigen', validators=[
        DataRequired(), 
        EqualTo('new_password', message='Passwörter müssen übereinstimmen')
    ])

class ChangeRoleForm(FlaskForm):
    """Rollen-Änderungsformular - Flag-basiert"""
    role = SelectField('Rolle', choices=[
        ('superadmin', 'Superadministrator'),
        ('admin', 'Administrator'),
        ('coach', 'Coach')
    ], validators=[DataRequired()])

class TrainerProfileForm(FlaskForm):
    """Trainer-Profil-Formular"""
    # Persönliche Daten
    license_number = StringField('Lizenznummer', validators=[Optional(), Length(max=50)])
    profile_image = FileField('Profilbild', validators=[Optional(), FileAllowed(['png', 'jpg', 'jpeg', 'gif'], 'Nur Bilddateien erlaubt')])
    first_name = StringField('Vorname', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Nachname', validators=[DataRequired(), Length(max=100)])
    street = StringField('Strasse', validators=[Optional(), Length(max=200)])
    postal_code = StringField('Postleitzahl', validators=[Optional(), Length(max=10)])
    city = StringField('Ort', validators=[Optional(), Length(max=100)])
    phone_private = StringField('Telefon privat', validators=[Optional(), Length(max=20)])
    phone_business = StringField('Telefon geschäftlich', validators=[Optional(), Length(max=20)])
    email_private = StringField('E-Mail privat', validators=[Optional(), Email(), Length(max=120)])
    email_business = StringField('E-Mail geschäftlich', validators=[Optional(), Email(), Length(max=120)])
    function_club = StringField('Aktuelle Funktion', validators=[Optional(), Length(max=200)])
    
    # CV
    cv_text = TextAreaField('Lebenslauf (Text)', validators=[Optional()])
    cv_file = FileField('Lebenslauf (Datei)', validators=[Optional(), FileAllowed(['pdf', 'doc', 'docx'], 'Nur PDF und Word-Dateien erlaubt')])

class CoachingExperienceForm(FlaskForm):
    """Coaching-Erfahrung Formular"""
    start_year = IntegerField('Startjahr', validators=[DataRequired(), NumberRange(min=1900, max=2100)])
    end_year = IntegerField('Endjahr (optional, leer lassen wenn laufend)', validators=[Optional(), NumberRange(min=1900, max=2100)])
    coaching_role = SelectField('Coaching-Rolle', choices=CoachingExperience.ROLES, validators=[DataRequired()])
    team = SelectField('Team', choices=CoachingExperience.TEAMS, validators=[DataRequired()])
    position = SelectField('Position (optional)', choices=CoachingExperience.POSITIONS, validators=[Optional()])
    
    def validate_end_year(self, end_year):
        """Prüft ob Endjahr nach Startjahr liegt (nur wenn angegeben)"""
        if self.start_year.data and end_year.data:
            if end_year.data < self.start_year.data:
                raise ValidationError('Das Endjahr muss nach dem Startjahr liegen.')

class CertificateForm(FlaskForm):
    """Zertifikat-Formular"""
    title = StringField('Titel', validators=[DataRequired(), Length(max=200)])
    issuer = StringField('Ausstellende Organisation', validators=[Optional(), Length(max=200)])
    issue_date = DateField('Ausstellungsdatum', validators=[Optional()])
    expiry_date = DateField('Ablaufdatum', validators=[Optional()])
    description = TextAreaField('Beschreibung', validators=[Optional()])
    file = FileField('Zertifikat-Datei', validators=[DataRequired(), FileAllowed(['pdf', 'png', 'jpg', 'jpeg', 'gif'], 'Nur PDF und Bilddateien erlaubt')])

