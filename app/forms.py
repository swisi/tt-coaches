from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, DateField, SelectField, TextAreaField, TimeField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError
from datetime import datetime

TEAMS = [
    ('Tigers Mens Varsity', 'Tigers Mens Varsity'),
    ('U19 Tackle', 'U19 Tackle'),
    ('U16 Tackle / Flag', 'U16 Tackle / Flag'),
    ('Ultimate Flag', 'Ultimate Flag'),
    ('U13 Flag', 'U13 Flag'),
    ('U8 Flag', 'U8 Flag'),
    ('Other', 'Other')
]

POSITIONS = [
    ('Head Coach', 'Head Coach'),
    ('Offensive Coordinator', 'Offensive Coordinator'),
    ('Defensive Coordinator', 'Defensive Coordinator'),
    ('Special Teams Coordinator', 'Special Teams Coordinator'),
    ('Position Coach', 'Position Coach'),
    ('Assistant Coach', 'Assistant Coach'),
    ('Other', 'Other')
]

ACTIVITY_TYPES = [
    ('prepractice', 'Prepractice'),
    ('team_wide', 'Team-Wide'),
    ('group_specific', 'Group-Specific'),
    ('position_specific', 'Position spezifisch'),
    ('special_teams', 'Special Teams')
]

WEEKDAYS = [
    (0, 'Montag'),
    (1, 'Dienstag'),
    (2, 'Mittwoch'),
    (3, 'Donnerstag'),
    (4, 'Freitag'),
    (5, 'Samstag'),
    (6, 'Sonntag')
]

GROUPS = ['OL', 'DL', 'LB', 'RB', 'TE', 'WR', 'DB', 'QB']

class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email(check_deliverability=False)])
    password = PasswordField('Passwort', validators=[DataRequired()])

class SignUpForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email(check_deliverability=False)])
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=8, message='Passwort muss mindestens 8 Zeichen lang sein')])
    password_confirm = PasswordField('Passwort bestätigen', validators=[DataRequired(), Length(min=8)])
    
    def validate_password_confirm(self, field):
        if field.data != self.password.data:
            raise ValidationError('Die Passwörter stimmen nicht überein.')

class ProfileForm(FlaskForm):
    first_name = StringField('Vorname', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Nachname', validators=[DataRequired(), Length(max=100)])
    birth_date = DateField('Geburtsdatum', validators=[DataRequired()])
    address = StringField('Straße & Hausnummer', validators=[DataRequired(), Length(max=200)])
    zip_code = StringField('PLZ', validators=[DataRequired(), Length(max=10)])
    city = StringField('Ort', validators=[DataRequired(), Length(max=100)])
    mobile_phone = StringField('Mobiltelefon', validators=[DataRequired(), Length(max=20)])
    team = SelectField('Team', choices=TEAMS, validators=[DataRequired()])
    license_number = StringField('Lizenznummer', validators=[Optional(), Length(max=50)])
    new_password = PasswordField('Neues Passwort (leer lassen = keine Änderung)', 
                                validators=[Optional(), Length(min=8, message='Passwort muss mindestens 8 Zeichen lang sein')])

class CertificateForm(FlaskForm):
    title = StringField('Titel des Zertifikats', validators=[DataRequired(), Length(max=200)])
    organization = StringField('Ausstellende Organisation', validators=[DataRequired(), Length(max=200)])
    acquisition_date = DateField('Erwerbsdatum', validators=[DataRequired()])
    valid_until = DateField('Gültig bis', validators=[Optional()])
    file = FileField('Zertifikatsdokument (PDF/Bild)', 
                    validators=[Optional(), FileAllowed(['pdf', 'png', 'jpg', 'jpeg'], 'Nur PDF, PNG, JPG erlaubt!')])

class ExperienceForm(FlaskForm):
    start_year = IntegerField('Startjahr', validators=[DataRequired()])
    end_year = IntegerField('Endjahr (leer lassen wenn laufend)', validators=[Optional()])
    team = SelectField('Team', choices=TEAMS, validators=[DataRequired()])
    position = SelectField('Position', choices=POSITIONS, validators=[DataRequired()])
    
    def validate_end_year(self, field):
        if field.data and field.data < self.start_year.data:
            raise ValidationError('Endjahr muss nach dem Startjahr liegen.')

class TrainingPlanForm(FlaskForm):
    title = StringField('Titel', validators=[DataRequired(), Length(max=200)])
    team_name = SelectField('Team', choices=TEAMS, validators=[DataRequired()])
    start_date = DateField('Startdatum', validators=[DataRequired()])
    end_date = DateField('Enddatum', validators=[DataRequired()])
    weekday = SelectField('Wochentag', choices=WEEKDAYS, coerce=int, validators=[DataRequired()])
    start_time = TimeField('Trainingsstart', validators=[DataRequired()])
    dresscode = StringField('Dresscode', validators=[Optional(), Length(max=200)])
    focus = TextAreaField('Trainingsfokus', validators=[Optional()])
    goals = TextAreaField('Ziele/Notizen', validators=[Optional()])
    
    def validate_end_date(self, field):
        if field.data and field.data < self.start_date.data:
            raise ValidationError('Enddatum muss nach dem Startdatum liegen.')

class TrainingActivityForm(FlaskForm):
    activity_name = StringField('Aktivitätsname', validators=[DataRequired(), Length(max=200)])
    activity_type = SelectField('Aktivitätstyp', choices=ACTIVITY_TYPES, validators=[DataRequired()], default='team_wide')
    duration_minutes = IntegerField('Dauer (Minuten)', validators=[DataRequired()])
    notes = TextAreaField('Notizen', validators=[Optional()])
    
    # Group checkboxes
    group_OL = BooleanField('OL', default=False)
    group_DL = BooleanField('DL', default=False)
    group_LB = BooleanField('LB', default=False)
    group_RB = BooleanField('RB', default=False)
    group_TE = BooleanField('TE', default=False)
    group_WR = BooleanField('WR', default=False)
    group_QB = BooleanField('QB', default=False)
    group_DB = BooleanField('DB', default=False)
    
    def get_groups_dict(self):
        """Konvertiert die Checkbox-Werte in ein Dictionary"""
        groups = {}
        for group in GROUPS:
            field_name = f'group_{group}'
            groups[group] = getattr(self, field_name).data
        return groups

class AdminUserForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email(check_deliverability=False)])
    first_name = StringField('Vorname', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Nachname', validators=[DataRequired(), Length(max=100)])
    birth_date = DateField('Geburtsdatum', validators=[DataRequired()])
    address = StringField('Straße & Hausnummer', validators=[DataRequired(), Length(max=200)])
    zip_code = StringField('PLZ', validators=[DataRequired(), Length(max=10)])
    city = StringField('Ort', validators=[DataRequired(), Length(max=100)])
    mobile_phone = StringField('Mobiltelefon', validators=[DataRequired(), Length(max=20)])
    team = SelectField('Team', choices=TEAMS, validators=[DataRequired()])
    license_number = StringField('Lizenznummer', validators=[Optional(), Length(max=50)])
    is_admin = BooleanField('Ist Administrator', default=False)
    new_password = PasswordField('Neues Passwort (leer lassen = keine Änderung)', 
                                validators=[Optional(), Length(min=8, message='Passwort muss mindestens 8 Zeichen lang sein')])

