from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
from ethiopian_utils import format_ethiopian_date

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'hr' or 'owner'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    employee_number = db.Column(db.Integer, unique=True, nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    age = db.Column(db.Integer, nullable=False)
    position = db.Column(db.String(100), nullable=False)
    education_background = db.Column(db.String(200))
    field_of_study = db.Column(db.String(200))
    employment_date = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(50))
    address = db.Column(db.String(300))
    factory_name = db.Column(db.String(100))
    salary = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, suspended, archived
    retirement_date = db.Column(db.Date, nullable=False)
    health_status = db.Column(db.String(20), default='normal')  # normal, abnormal
    health_details = db.Column(db.Text)  # JSON string
    emer_name = db.Column(db.String(200))
    emer_phone = db.Column(db.String(50))
    suspension_start_date = db.Column(db.Date)
    suspension_days = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    attendance_logs = db.relationship('AttendanceLog', backref='employee', lazy=True, cascade='all, delete-orphan')
    leave_used_logs = db.relationship('LeaveUsedLog', backref='employee', lazy=True, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='employee', lazy=True, cascade='all, delete-orphan')

    def calculate_age(self):
        """Calculate current age from birth_date dynamically"""
        if not self.birth_date:
            return self.age  # Fallback to stored age
        from datetime import date
        today = date.today()
        # Precise age calculation considering month and day
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    def to_dict(self):
        health_details_obj = None
        if self.health_details:
            try:
                health_details_obj = json.loads(self.health_details)
                # Add Ethiopian date to health details if diagnosis_date exists
                if health_details_obj.get('diagnosis_date'):
                    try:
                        from datetime import datetime as dt
                        diag_date = dt.strptime(health_details_obj['diagnosis_date'], '%Y-%m-%d').date()
                        health_details_obj['diagnosis_date_eth'] = format_ethiopian_date(diag_date)
                    except:
                        pass
            except:
                health_details_obj = None
        
        return {
            'id': self.id,
            'employee_number': self.employee_number,
            'full_name': self.full_name,
            'gender': self.gender,
            'age': self.calculate_age() if self.birth_date else self.age,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'birth_date_eth': format_ethiopian_date(self.birth_date) if self.birth_date else '',
            'position': self.position,
            'education_background': self.education_background,
            'field_of_study': self.field_of_study,
            'employment_date': self.employment_date.isoformat() if self.employment_date else None,
            'employment_date_eth': format_ethiopian_date(self.employment_date),
            'phone': self.phone,
            'address': self.address,
            'factory_name': self.factory_name,
            'salary': float(self.salary) if self.salary else 0,
            'status': self.status,
            'retirement_date': self.retirement_date.isoformat() if self.retirement_date else None,
            'retirement_date_eth': format_ethiopian_date(self.retirement_date),
            'health_status': self.health_status,
            'health_details': health_details_obj,
            'emer_name': self.emer_name,
            'emer_phone': self.emer_phone,
            'suspension_start_date': self.suspension_start_date.isoformat() if self.suspension_start_date else None,
            'suspension_days': self.suspension_days
        }

class AttendanceLog(db.Model):
    __tablename__ = 'attendance_logs'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    action = db.Column(db.String(10), nullable=False)  # 'in' or 'out'
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.full_name if self.employee else None,
            'employee_number': self.employee.employee_number if self.employee else None,
            'date': self.date.isoformat(),
            'date_eth': format_ethiopian_date(self.date),
            'action': self.action,
            'timestamp': self.timestamp.isoformat(),
            'time': self.timestamp.strftime('%H:%M')
        }

class LeaveUsedLog(db.Model):
    __tablename__ = 'leave_used_log'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    days_used = db.Column(db.Numeric(5, 2), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    recorder = db.relationship('User', backref='leave_records')
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.full_name if self.employee else None,
            'employee_number': self.employee.employee_number if self.employee else None,
            'days_used': float(self.days_used),
            'reason': self.reason,
            'recorded_by': self.recorder.username if self.recorder else None,
            'recorded_at': self.recorded_at.isoformat()
        }

class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'message': self.message,
            'submitted_at': self.submitted_at.isoformat()
        }

class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    employee_number = db.Column(db.Integer)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    changer = db.relationship('User', backref='audit_entries')
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_number': self.employee_number,
            'action': self.action,
            'details': self.details,
            'changed_by': self.changer.username if self.changer else None,
            'timestamp': self.timestamp.isoformat()
        }
