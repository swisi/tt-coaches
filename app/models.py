from datetime import datetime, timedelta
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    license_number = db.Column(db.String(50))
    mobile_phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    zip_code = db.Column(db.String(10))
    city = db.Column(db.String(100))
    birth_date = db.Column(db.Date)
    team = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    certificates = db.relationship('Certificate', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    experiences = db.relationship('Experience', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_profile_complete(self):
        required_fields = [
            self.first_name, self.last_name, self.birth_date,
            self.address, self.zip_code, self.city, self.mobile_phone, self.team
        ]
        return all(field is not None and field != '' for field in required_fields)
    
    def get_total_experience_years(self):
        experiences = self.experiences.all()
        if not experiences:
            return 0
        
        total_days = 0
        for exp in experiences:
            start = datetime(exp.start_year, 1, 1)
            end = datetime(exp.end_year, 12, 31) if exp.end_year else datetime.now()
            total_days += (end - start).days
        
        return int(round(total_days / 365.25))
    
    def __repr__(self):
        return f'<User {self.email}>'

class Certificate(db.Model):
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    organization = db.Column(db.String(200), nullable=False)
    acquisition_date = db.Column(db.Date, nullable=False)
    valid_until = db.Column(db.Date)
    file_url = db.Column(db.String(500))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_expired(self):
        if not self.valid_until:
            return False
        return self.valid_until < datetime.now().date()
    
    def expires_soon(self, days=30):
        if not self.valid_until:
            return False
        return datetime.now().date() <= self.valid_until <= (datetime.now().date() + timedelta(days=days))
    
    def __repr__(self):
        return f'<Certificate {self.title}>'

class Experience(db.Model):
    __tablename__ = 'experiences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_year = db.Column(db.Integer, nullable=False)
    end_year = db.Column(db.Integer)
    team = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_current(self):
        return self.end_year is None
    
    def __repr__(self):
        return f'<Experience {self.team} {self.start_year}>'

class TrainingPlan(db.Model):
    __tablename__ = 'training_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    team_name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    weekday = db.Column(db.Integer, nullable=False)  # 0=Montag, 6=Sonntag
    start_time = db.Column(db.Time, nullable=False)
    dresscode = db.Column(db.String(200))
    focus = db.Column(db.Text)
    goals = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    activities = db.relationship('TrainingActivity', backref='plan', lazy='dynamic', 
                                order_by='TrainingActivity.order', cascade='all, delete-orphan')
    
    def get_weekday_name(self):
        weekdays = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
        return weekdays[self.weekday]
    
    def is_active_today(self):
        today = datetime.now().date()
        weekday = today.weekday()  # 0=Montag
        return (self.start_date <= today <= self.end_date) and (self.weekday == weekday)
    
    def get_weekday_color(self):
        colors = {
            0: 'blue',    # Montag
            1: 'green',   # Dienstag
            2: 'purple',  # Mittwoch
            3: 'amber',   # Donnerstag
            4: 'pink',    # Freitag
            5: 'cyan',    # Samstag
            6: 'red'      # Sonntag
        }
        return colors.get(self.weekday, 'gray')
    
    def __repr__(self):
        return f'<TrainingPlan {self.title}>'

class TrainingActivity(db.Model):
    __tablename__ = 'training_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('training_plans.id'), nullable=False)
    time_from = db.Column(db.Time, nullable=False)
    time_to = db.Column(db.Time, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    activity_name = db.Column(db.String(200), nullable=False)  # Für team_wide, prepractice, special_teams
    activity_type = db.Column(db.String(50), nullable=False)  # prepractice, team_wide, group_specific, special_teams
    groups = db.Column(db.JSON)  # {OL: true, DL: false, ...} - welche Gruppen aktiv sind
    group_activities = db.Column(db.JSON)  # {"OL,DL": "OL/DL ST Line", "LB,RB": "LB & RB"} - Aktivitätsnamen pro Gruppenkombination
    notes = db.Column(db.Text)
    order = db.Column(db.Integer, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_active_groups(self):
        if not self.groups:
            return []
        return [group for group, active in self.groups.items() if active]
    
    def get_group_combinations(self):
        """
        Gibt die Gruppenkombinationen in der richtigen Reihenfolge zurück.
        Returns: List of tuples (group_list, activity_name)
        """
        if self.activity_type != 'group_specific' or not self.group_activities:
            return []
        
        GROUPS_ORDER = ['OL', 'DL', 'LB', 'RB', 'TE', 'WR', 'QB', 'DB']
        
        # Konvertiere group_activities dict in Liste von Tupeln
        combinations = []
        for key, activity_name in self.group_activities.items():
            groups = [g.strip() for g in key.split(',')]
            # Sortiere Gruppen nach GROUPS_ORDER
            groups.sort(key=lambda g: GROUPS_ORDER.index(g) if g in GROUPS_ORDER else 999)
            combinations.append((groups, activity_name))
        
        # Sortiere Kombinationen nach der ersten Gruppe
        combinations.sort(key=lambda x: GROUPS_ORDER.index(x[0][0]) if x[0] and x[0][0] in GROUPS_ORDER else 999)
        
        return combinations
    
    def get_group_cells(self):
        """
        Gibt eine Liste von Zellen für die Gruppen-Spalten zurück.
        Jede Zelle ist ein Dict mit 'colspan', 'text', 'groups'
        """
        GROUPS_ORDER = ['OL', 'DL', 'LB', 'RB', 'TE', 'WR', 'QB', 'DB']
        
        if self.activity_type == 'team_wide' or self.activity_type == 'prepractice' or self.activity_type == 'special_teams':
            # Alle Gruppen zusammen
            return [{'colspan': 8, 'text': self.activity_name, 'groups': GROUPS_ORDER}]
        
        if self.activity_type == 'group_specific' and self.group_activities:
            # Erstelle Mapping von Gruppe zu Aktivitätsname
            group_to_activity = {}
            for key, activity_name in self.group_activities.items():
                groups = [g.strip() for g in key.split(',')]
                for group in groups:
                    if group in GROUPS_ORDER:
                        group_to_activity[group] = activity_name
            
            # Erstelle Zellen mit merged cells
            cells = []
            i = 0
            while i < len(GROUPS_ORDER):
                group = GROUPS_ORDER[i]
                if group in group_to_activity:
                    # Finde alle aufeinanderfolgenden Gruppen mit demselben Text
                    activity_text = group_to_activity[group]
                    span_groups = [group]
                    j = i + 1
                    while j < len(GROUPS_ORDER) and GROUPS_ORDER[j] in group_to_activity and group_to_activity[GROUPS_ORDER[j]] == activity_text:
                        span_groups.append(GROUPS_ORDER[j])
                        j += 1
                    
                    cells.append({
                        'colspan': len(span_groups),
                        'text': activity_text,
                        'groups': span_groups
                    })
                    i = j
                else:
                    # Keine Aktivität für diese Gruppe
                    cells.append({
                        'colspan': 1,
                        'text': '-',
                        'groups': [group]
                    })
                    i += 1
            
            return cells
        
        # Fallback: Einzelne Checkmarks
        cells = []
        for group in GROUPS_ORDER:
            active = self.groups and self.groups.get(group, False)
            cells.append({
                'colspan': 1,
                'text': '✓' if active else '-',
                'groups': [group]
            })
        return cells
    
    def get_activity_type_color(self):
        colors = {
            'prepractice': 'amber',
            'team_wide': 'purple',
            'group_specific': 'blue',
            'special_teams': 'green'
        }
        return colors.get(self.activity_type, 'gray')
    
    def __repr__(self):
        return f'<TrainingActivity {self.activity_name}>'

