from flask import Flask, request, jsonify, session, render_template, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from models import db, User, Employee, AttendanceLog, LeaveUsedLog, ContactMessage, AuditLog
from ethiopian_utils import ethiopian_to_gregorian, gregorian_to_ethiopian, format_ethiopian_date, parse_ethiopian_date
import json
import os
import pandas as pd
import io

app = Flask(__name__, static_folder='.')
app.config['SECRET_KEY'] = 'victory-water-happy-juice-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:wisdomlife1%40@localhost/victory_hr'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
CORS(app, supports_credentials=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database and seed users
def init_db():
    with app.app_context():
        db.create_all()
        
        # Seed default users if not exists
        if not User.query.filter_by(username='hr').first():
            hr_user = User(username='hr', role='hr')
            hr_user.set_password('hr123')
            db.session.add(hr_user)
        
        if not User.query.filter_by(username='owner').first():
            owner_user = User(username='owner', role='owner')
            owner_user.set_password('owner123')
            db.session.add(owner_user)
        
        db.session.commit()
        print("Database initialized with default users!")

# Helper function: Calculate leave balance
def calculate_leave_balance(employee):
    today = date.today()
    emp_date = employee.employment_date
    
    # Calculate actual days employed
    total_days = (today - emp_date).days
    total_days -= (employee.suspension_days or 0)
    
    # If currently suspended, subtract current suspension period
    if employee.status == 'suspended' and employee.suspension_start_date:
        susp_days = (today - employee.suspension_start_date).days
        total_days -= susp_days
    
    total_days = max(0, total_days)
    
    # Calculate years of service
    years_service = int(total_days / 365.25)
    
    # Annual entitlement
    annual_entitlement = 16 + int(max(0, years_service - 1) / 2)
    
    # Accrued
    accrued = (annual_entitlement / 365.25) * total_days
    
    # Used days
    used = sum(float(log.days_used) for log in employee.leave_used_logs)
    
    # Balance
    balance = accrued - used
    
    return {
        'years_service': years_service,
        'annual_entitlement': annual_entitlement,
        'accrued': round(accrued, 2),
        'used': round(used, 2),
        'balance': round(balance, 2)
    }

# Helper function: Add audit log
def add_audit_log(employee_number, action, details):
    audit = AuditLog(
        employee_number=employee_number,
        action=action,
        details=details,
        changed_by=current_user.id
    )
    db.session.add(audit)

# ===== ROUTES =====

# Serve HTML files
@app.route('/')
def index():
    return send_from_directory('.', 'login.html')

@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory('.', path)

# ===== AUTH ROUTES =====

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username', '').lower()
    password = data.get('password', '')
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        login_user(user)
        return jsonify({
            'success': True,
            'role': user.role,
            'username': user.username
        })
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({'success': True})

@app.route('/api/current-user', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({
        'username': current_user.username,
        'role': current_user.role
    })

# ===== EMPLOYEE ROUTES =====

@app.route('/api/employees', methods=['GET'])
@login_required
def get_employees():
    search = request.args.get('search', '').lower()
    status = request.args.get('status', '')
    
    query = Employee.query
    
    if search:
        query = query.filter(
            db.or_(
                Employee.full_name.ilike(f'%{search}%'),
                Employee.position.ilike(f'%{search}%'),
                db.cast(Employee.employee_number, db.String).ilike(f'%{search}%')
            )
        )
    
    if status:
        query = query.filter_by(status=status)
    
    employees = query.order_by(Employee.employee_number).all()
    return jsonify([emp.to_dict() for emp in employees])

@app.route('/api/employees', methods=['POST'])
@login_required
def create_employee():
    data = request.json
    
    # Check if employee number exists
    if Employee.query.filter_by(employee_number=data['employee_number']).first():
        return jsonify({'success': False, 'message': 'Employee number already exists'}), 400
    
    # Parse employment date (Ethiopian or Gregorian)
    employment_date_str = data.get('employment_date_eth') or data.get('employment_date')
    if employment_date_str:
        employment_date = parse_ethiopian_date(employment_date_str)
        if not employment_date:
            try:
                employment_date = datetime.strptime(employment_date_str, '%Y-%m-%d').date()
            except:
                return jsonify({'success': False, 'message': 'Invalid employment date format'}), 400
    else:
        return jsonify({'success': False, 'message': 'Employment date is required'}), 400
    
    # Calculate birth_date from age and employment_date
    age = int(data['age'])
    birth_date = employment_date - relativedelta(years=age)
    
    # Calculate retirement_date as birth_date + 60 years
    retirement_date = birth_date + relativedelta(years=60)
    
    # Parse health details
    health_details = None
    if data.get('health_status') == 'abnormal' and data.get('health_details'):
        health_details_obj = data['health_details']
        # Convert diagnosis date if present
        if health_details_obj.get('diagnosis_date_eth'):
            diag_date = parse_ethiopian_date(health_details_obj['diagnosis_date_eth'])
            health_details_obj['diagnosis_date'] = diag_date.isoformat() if diag_date else None
        elif health_details_obj.get('diagnosis_date'):
            try:
                diag_date = datetime.strptime(health_details_obj['diagnosis_date'], '%Y-%m-%d').date()
                health_details_obj['diagnosis_date'] = diag_date.isoformat()
            except:
                pass
        health_details = json.dumps(health_details_obj)
    
    employee = Employee(
        employee_number=data['employee_number'],
        full_name=data['full_name'],
        gender=data['gender'],
        birth_date=birth_date,
        age=age,
        position=data['position'],
        education_background=data.get('education_background'),
        field_of_study=data.get('field_of_study'),
        employment_date=employment_date,
        phone=data.get('phone'),
        address=data.get('address'),
        factory_name=data.get('factory_name'),
        salary=data['salary'],
        status=data.get('status', 'active'),
        retirement_date=retirement_date,
        health_status=data.get('health_status', 'normal'),
        health_details=health_details,
        emer_name=data.get('emer_name'),
        emer_phone=data.get('emer_phone')
    )
    
    db.session.add(employee)
    db.session.commit()
    
    add_audit_log(employee.employee_number, 'Added', f'Employee {employee.full_name} added')
    db.session.commit()
    
    return jsonify({'success': True, 'employee': employee.to_dict()})

@app.route('/api/employees/<int:emp_id>', methods=['PUT'])
@login_required
def update_employee(emp_id):
    employee = Employee.query.get_or_404(emp_id)
    data = request.json
    
    # Check if employee number is being changed and if it exists
    if data['employee_number'] != employee.employee_number:
        if Employee.query.filter_by(employee_number=data['employee_number']).first():
            return jsonify({'success': False, 'message': 'Employee number already exists'}), 400
    
    # Parse employment date (Ethiopian or Gregorian)
    employment_date_str = data.get('employment_date_eth') or data.get('employment_date')
    if employment_date_str:
        employment_date = parse_ethiopian_date(employment_date_str)
        if not employment_date:
            try:
                employment_date = datetime.strptime(employment_date_str, '%Y-%m-%d').date()
            except:
                employment_date = employee.employment_date
    else:
        employment_date = employee.employment_date
    
    # Calculate birth_date from age and employment_date
    age = int(data['age'])
    birth_date = employment_date - relativedelta(years=age)
    
    # Calculate retirement_date as birth_date + 60 years
    retirement_date = birth_date + relativedelta(years=60)
    
    # Parse health details
    health_details = None
    if data.get('health_status') == 'abnormal' and data.get('health_details'):
        health_details_obj = data['health_details']
        # Convert diagnosis date if present
        if health_details_obj.get('diagnosis_date_eth'):
            diag_date = parse_ethiopian_date(health_details_obj['diagnosis_date_eth'])
            health_details_obj['diagnosis_date'] = diag_date.isoformat() if diag_date else None
        elif health_details_obj.get('diagnosis_date'):
            try:
                diag_date = datetime.strptime(health_details_obj['diagnosis_date'], '%Y-%m-%d').date()
                health_details_obj['diagnosis_date'] = diag_date.isoformat()
            except:
                pass
        health_details = json.dumps(health_details_obj)
    
    employee.employee_number = data['employee_number']
    employee.full_name = data['full_name']
    employee.gender = data['gender']
    employee.birth_date = birth_date
    employee.age = age
    employee.position = data['position']
    employee.education_background = data.get('education_background')
    employee.field_of_study = data.get('field_of_study')
    employee.employment_date = employment_date
    employee.phone = data.get('phone')
    employee.address = data.get('address')
    employee.factory_name = data.get('factory_name')
    employee.salary = data['salary']
    employee.status = data.get('status', 'active')
    employee.retirement_date = retirement_date
    employee.health_status = data.get('health_status', 'normal')
    employee.health_details = health_details
    employee.emer_name = data.get('emer_name')
    employee.emer_phone = data.get('emer_phone')
    
    db.session.commit()
    
    add_audit_log(employee.employee_number, 'Updated', f'Employee {employee.full_name} updated')
    db.session.commit()
    
    return jsonify({'success': True, 'employee': employee.to_dict()})

@app.route('/api/employees/<int:emp_id>/suspend', methods=['POST'])
@login_required
def suspend_employee(emp_id):
    employee = Employee.query.get_or_404(emp_id)
    employee.status = 'suspended'
    employee.suspension_start_date = date.today()
    
    db.session.commit()
    
    add_audit_log(employee.employee_number, 'Suspended', f'Employee {employee.full_name} suspended')
    db.session.commit()
    
    return jsonify({'success': True, 'employee': employee.to_dict()})

@app.route('/api/employees/<int:emp_id>/reactivate', methods=['POST'])
@login_required
def reactivate_employee(emp_id):
    employee = Employee.query.get_or_404(emp_id)
    
    # Calculate suspension days
    if employee.suspension_start_date:
        days = (date.today() - employee.suspension_start_date).days
        employee.suspension_days += days
        employee.suspension_start_date = None
    
    employee.status = 'active'
    db.session.commit()
    
    add_audit_log(employee.employee_number, 'Reactivated', f'Employee {employee.full_name} reactivated')
    db.session.commit()
    
    return jsonify({'success': True, 'employee': employee.to_dict()})

@app.route('/api/employees/<int:emp_id>/archive', methods=['POST'])
@login_required
def archive_employee(emp_id):
    employee = Employee.query.get_or_404(emp_id)
    employee.status = 'archived'
    
    db.session.commit()
    
    add_audit_log(employee.employee_number, 'Archived', f'Employee {employee.full_name} archived')
    db.session.commit()
    
    return jsonify({'success': True, 'employee': employee.to_dict()})

@app.route('/api/employees/<int:emp_id>/health', methods=['PUT'])
@login_required
def update_health(emp_id):
    employee = Employee.query.get_or_404(emp_id)
    data = request.json
    
    old_status = employee.health_status
    employee.health_status = data.get('health_status', 'normal')
    
    health_details = None
    if data.get('health_status') == 'abnormal' and data.get('health_details'):
        health_details_obj = data['health_details']
        # Convert diagnosis date if present
        if health_details_obj.get('diagnosis_date_eth'):
            diag_date = parse_ethiopian_date(health_details_obj['diagnosis_date_eth'])
            health_details_obj['diagnosis_date'] = diag_date.isoformat() if diag_date else None
        elif health_details_obj.get('diagnosis_date'):
            try:
                diag_date = datetime.strptime(health_details_obj['diagnosis_date'], '%Y-%m-%d').date()
                health_details_obj['diagnosis_date'] = diag_date.isoformat()
            except:
                pass
        health_details = json.dumps(health_details_obj)
    
    employee.health_details = health_details
    
    db.session.commit()
    
    add_audit_log(employee.employee_number, 'Health Status Updated', 
                  f'Health status changed from {old_status} to {employee.health_status}')
    db.session.commit()
    
    return jsonify({'success': True, 'employee': employee.to_dict()})

# ===== ATTENDANCE ROUTES =====

@app.route('/api/attendance/kiosk', methods=['POST'])
def attendance_kiosk():
    """Public endpoint for attendance kiosk - no login required"""
    data = request.json
    employee_number = data.get('employee_number')
    action = data.get('action')  # 'in' or 'out'
    
    employee = Employee.query.filter_by(employee_number=employee_number).first()
    if not employee:
        return jsonify({'success': False, 'message': 'Employee not found'}), 404
    
    if employee.status != 'active':
        return jsonify({'success': False, 'message': f'Employee is {employee.status}'}), 400
    
    today = date.today()
    
    # Check if already checked in/out today
    existing = AttendanceLog.query.filter_by(
        employee_id=employee.id,
        date=today,
        action=action
    ).first()
    
    if existing:
        return jsonify({'success': False, 'message': f'Already checked {action} today'}), 400
    
    # If checking out, must have checked in first
    if action == 'out':
        check_in = AttendanceLog.query.filter_by(
            employee_id=employee.id,
            date=today,
            action='in'
        ).first()
        
        if not check_in:
            return jsonify({'success': False, 'message': 'Must check in first'}), 400
    
    # Create attendance log with server timestamp
    log = AttendanceLog(
        employee_id=employee.id,
        date=today,
        action=action,
        timestamp=datetime.now()
    )
    
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'{employee.full_name} checked {action} successfully',
        'log': log.to_dict()
    })

@app.route('/api/attendance/logs', methods=['GET'])
@login_required
def get_attendance_logs():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    employee_id = request.args.get('employee_id')
    
    query = AttendanceLog.query
    
    if start_date:
        query = query.filter(AttendanceLog.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    
    if end_date:
        query = query.filter(AttendanceLog.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    if employee_id:
        query = query.filter_by(employee_id=int(employee_id))
    
    logs = query.order_by(AttendanceLog.date.desc(), AttendanceLog.timestamp.desc()).all()
    return jsonify([log.to_dict() for log in logs])

# ===== LEAVE ROUTES =====

@app.route('/api/leave/balances', methods=['GET'])
@login_required
def get_leave_balances():
    employees = Employee.query.filter(Employee.status != 'archived').all()
    
    balances = []
    for emp in employees:
        balance_data = calculate_leave_balance(emp)
        balances.append({
            'employee_id': emp.id,
            'employee_number': emp.employee_number,
            'full_name': emp.full_name,
            'accrued': balance_data['accrued'],
            'used': balance_data['used'],
            'balance': balance_data['balance'],
            'years_service': balance_data['years_service'],
            'annual_entitlement': balance_data['annual_entitlement']
        })
    
    return jsonify(balances)

@app.route('/api/leave/used', methods=['POST'])
@login_required
def add_leave_used():
    data = request.json
    employee_id = data.get('employee_id')
    days_used = data.get('days_used')
    reason = data.get('reason')
    
    employee = Employee.query.get_or_404(employee_id)
    
    # Validate balance
    balance_data = calculate_leave_balance(employee)
    if balance_data['balance'] < float(days_used):
        return jsonify({
            'success': False,
            'message': f'Insufficient balance. Available: {balance_data["balance"]} days, Requested: {days_used} days'
        }), 400
    
    log = LeaveUsedLog(
        employee_id=employee_id,
        days_used=days_used,
        reason=reason,
        recorded_by=current_user.id
    )
    
    db.session.add(log)
    db.session.commit()
    
    add_audit_log(employee.employee_number, 'Leave Used Added', 
                  f'{days_used} days used for {employee.full_name}: {reason}')
    db.session.commit()
    
    return jsonify({'success': True, 'log': log.to_dict()})

@app.route('/api/leave/used/history', methods=['GET'])
@login_required
def get_leave_history():
    employee_id = request.args.get('employee_id')
    
    query = LeaveUsedLog.query
    if employee_id:
        query = query.filter_by(employee_id=int(employee_id))
    
    logs = query.order_by(LeaveUsedLog.recorded_at.desc()).all()
    return jsonify([log.to_dict() for log in logs])

# ===== CONTACT MESSAGE ROUTES =====

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    """Public endpoint - no login required"""
    data = request.json
    
    message = ContactMessage(
        name=data['name'],
        email=data['email'],
        message=data['message']
    )
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Message sent successfully'})

@app.route('/api/messages', methods=['GET'])
@login_required
def get_messages():
    messages = ContactMessage.query.order_by(ContactMessage.submitted_at.desc()).all()
    return jsonify([msg.to_dict() for msg in messages])

@app.route('/api/messages/<int:msg_id>', methods=['DELETE'])
@login_required
def delete_message(msg_id):
    message = ContactMessage.query.get_or_404(msg_id)
    db.session.delete(message)
    db.session.commit()
    return jsonify({'success': True})

# ===== AUDIT LOG ROUTES =====

@app.route('/api/audit', methods=['GET'])
@login_required
def get_audit_log():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    return jsonify([log.to_dict() for log in logs])

# ===== OWNER METRICS ROUTES =====

@app.route('/api/owner/metrics', methods=['GET'])
@login_required
def get_owner_metrics():
    today = date.today()
    
    # Active employees count
    active_count = Employee.query.filter_by(status='active').count()
    
    # Today's attendance
    today_logs = AttendanceLog.query.filter_by(date=today).all()
    
    checked_in = set()
    for log in today_logs:
        if log.action == 'in':
            checked_in.add(log.employee_id)
    
    # Late arrivals (after 08:15)
    late_count = 0
    for log in today_logs:
        if log.action == 'in':
            time_str = log.timestamp.strftime('%H:%M')
            if time_str > '08:15':
                late_count += 1
    
    # Absent today
    absent_count = active_count - len(checked_in)
    
    # Missing checkouts from yesterday
    yesterday = today - timedelta(days=1)
    yesterday_logs = AttendanceLog.query.filter_by(date=yesterday).all()
    
    yesterday_in = set()
    yesterday_out = set()
    for log in yesterday_logs:
        if log.action == 'in':
            yesterday_in.add(log.employee_id)
        elif log.action == 'out':
            yesterday_out.add(log.employee_id)
    
    missing_checkout_ids = yesterday_in - yesterday_out
    missing_checkouts = []
    for emp_id in missing_checkout_ids:
        emp = Employee.query.get(emp_id)
        if emp:
            missing_checkouts.append({
                'employee_number': emp.employee_number,
                'full_name': emp.full_name
            })
    
    return jsonify({
        'active_employees': active_count,
        'checked_in_today': len(checked_in),
        'late_today': late_count,
        'absent_today': absent_count,
        'missing_checkouts': missing_checkouts
    })

# ===== ETHIOPIAN CALENDAR CONVERSION ROUTES =====

@app.route('/api/convert/eth_to_greg', methods=['POST'])
@login_required
def convert_eth_to_greg():
    """Convert Ethiopian date to Gregorian date"""
    data = request.json
    eth_date = data.get('ethiopian_date')  # Expected format: YYYY-MM-DD
    
    if not eth_date:
        return jsonify({'success': False, 'message': 'Ethiopian date is required'}), 400
    
    greg_date = parse_ethiopian_date(eth_date)
    
    if not greg_date:
        return jsonify({'success': False, 'message': 'Invalid Ethiopian date format'}), 400
    
    return jsonify({
        'success': True,
        'ethiopian_date': eth_date,
        'gregorian_date': greg_date.isoformat()
    })

@app.route('/api/convert/greg_to_eth', methods=['POST'])
@login_required
def convert_greg_to_eth():
    """Convert Gregorian date to Ethiopian date"""
    data = request.json
    greg_date_str = data.get('gregorian_date')  # Expected format: YYYY-MM-DD
    
    if not greg_date_str:
        return jsonify({'success': False, 'message': 'Gregorian date is required'}), 400
    
    try:
        greg_date = datetime.strptime(greg_date_str, '%Y-%m-%d').date()
    except:
        return jsonify({'success': False, 'message': 'Invalid Gregorian date format'}), 400
    
    eth_date = format_ethiopian_date(greg_date)
    
    if not eth_date:
        return jsonify({'success': False, 'message': 'Date conversion failed'}), 400
    
    return jsonify({
        'success': True,
        'gregorian_date': greg_date_str,
        'ethiopian_date': eth_date
    })

# ===== BULK IMPORT ROUTE =====

@app.route('/api/employees/import', methods=['POST'])
@login_required
def import_employees():
    """Bulk import employees from CSV/Excel file"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    try:
        # Read file based on extension
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return jsonify({'success': False, 'message': 'Unsupported file format. Use CSV or Excel'}), 400
        
        # Expected columns (flexible - Ethiopian or Gregorian dates)
        required_cols = ['employee_number', 'full_name', 'gender', 'age', 'position', 'salary']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            return jsonify({'success': False, 'message': f'Missing required columns: {", ".join(missing_cols)}'}), 400
        
        imported_count = 0
        skipped_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Check if employee number exists
                emp_number = int(row['employee_number'])
                if Employee.query.filter_by(employee_number=emp_number).first():
                    skipped_count += 1
                    errors.append(f'Row {index+2}: Employee #{emp_number} already exists')
                    continue
                
                # Parse employment date (try Ethiopian first, then Gregorian)
                employment_date = None
                if 'employment_date_eth' in row and pd.notna(row['employment_date_eth']):
                    employment_date = parse_ethiopian_date(str(row['employment_date_eth']))
                elif 'employment_date' in row and pd.notna(row['employment_date']):
                    try:
                        employment_date = pd.to_datetime(row['employment_date']).date()
                    except:
                        pass
                
                if not employment_date:
                    skipped_count += 1
                    errors.append(f'Row {index+2}: Invalid or missing employment date')
                    continue
                
                # Calculate retirement date from age and employment date
                age = int(row['age'])
                birth_date = employment_date - relativedelta(years=age)
                retirement_date = birth_date + relativedelta(years=60)
                
                # Parse health details if abnormal
                health_status = str(row.get('health_status', 'normal')).lower()
                health_details = None
                
                if health_status == 'abnormal':
                    health_details_obj = {}
                    if 'disease' in row and pd.notna(row['disease']):
                        health_details_obj['disease'] = str(row['disease'])
                    
                    # Parse diagnosis date
                    if 'diagnosis_date_eth' in row and pd.notna(row['diagnosis_date_eth']):
                        diag_date = parse_ethiopian_date(str(row['diagnosis_date_eth']))
                        health_details_obj['diagnosis_date'] = diag_date.isoformat() if diag_date else None
                    elif 'diagnosis_date' in row and pd.notna(row['diagnosis_date']):
                        try:
                            diag_date = pd.to_datetime(row['diagnosis_date']).date()
                            health_details_obj['diagnosis_date'] = diag_date.isoformat()
                        except:
                            pass
                    
                    if 'health_notes' in row and pd.notna(row['health_notes']):
                        health_details_obj['notes'] = str(row['health_notes'])
                    
                    health_details = json.dumps(health_details_obj)
                
                # Create employee
                employee = Employee(
                    employee_number=emp_number,
                    full_name=str(row['full_name']),
                    gender=str(row['gender']),
                    birth_date=birth_date,
                    age=age,
                    position=str(row['position']),
                    education_background=str(row.get('education_background', '')) if pd.notna(row.get('education_background')) else None,
                    field_of_study=str(row.get('field_of_study', '')) if pd.notna(row.get('field_of_study')) else None,
                    employment_date=employment_date,
                    phone=str(row.get('phone', '')) if pd.notna(row.get('phone')) else None,
                    address=str(row.get('address', '')) if pd.notna(row.get('address')) else None,
                    factory_name=str(row.get('factory_name', '')) if pd.notna(row.get('factory_name')) else None,
                    salary=float(row['salary']),
                    status=str(row.get('status', 'active')).lower(),
                    retirement_date=retirement_date,
                    health_status=health_status,
                    health_details=health_details,
                    emer_name=str(row.get('emer_name', '')) if pd.notna(row.get('emer_name')) else None,
                    emer_phone=str(row.get('emer_phone', '')) if pd.notna(row.get('emer_phone')) else None
                )
                
                db.session.add(employee)
                imported_count += 1
                
            except Exception as e:
                skipped_count += 1
                errors.append(f'Row {index+2}: {str(e)}')
        
        # Commit all imports
        db.session.commit()
        
        # Add audit log
        add_audit_log(0, 'Bulk Import', f'Imported {imported_count} employees, skipped {skipped_count}')
        db.session.commit()
        
        return jsonify({
            'success': True,
            'imported': imported_count,
            'skipped': skipped_count,
            'errors': errors[:10]  # Return first 10 errors only
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Import failed: {str(e)}'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
