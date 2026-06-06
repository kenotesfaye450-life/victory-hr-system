# Victory Water & Happy Juice - HR Management System

A comprehensive HR management system built with Flask and PostgreSQL, featuring Ethiopian calendar support, attendance tracking, leave management, and health monitoring.

## Features

### Core Functionality
- **Employee Management**: Complete CRUD operations with wide table view (17 fields)
- **Ethiopian Calendar Toggle**: Switch between Ethiopian and Gregorian calendar displays
- **Attendance Tracking**: Kiosk-style check-in/out system with late arrival detection
- **Leave Management**: Automatic leave balance calculation based on employment duration
- **Health Status Monitoring**: Track employee health conditions and diagnosis dates
- **Audit Logging**: Complete audit trail of all system changes
- **CSV/Excel Import**: Bulk employee import with Ethiopian date conversion

### Technical Features
- Dynamic age calculation from birth date
- Automatic retirement date calculation (birth date + 60 years)
- Suspension days tracking for accurate leave calculations
- Role-based access control (HR and Owner roles)
- Responsive design with modern UI
- PostgreSQL database with proper foreign key relationships

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Git

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/kenotesfaye450/victory-hr-system.git
   cd victory-hr-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database**
   - Create PostgreSQL database:
     ```sql
     CREATE DATABASE victory_hr;
     ```
   - Update connection string in `app.py`:
     ```python
     app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/victory_hr'
     ```

5. **Run the application**
   ```bash
   python app.py
   ```
   Or on Windows:
   ```cmd
   run.bat
   ```

6. **Access the system**
   - Open browser: `http://localhost:5000`
   - Default credentials:
     - HR: `hr` / `hr123`
     - Owner: `owner` / `owner123`

## Project Structure

```
Victorywater/
├── app.py                      # Main Flask application
├── models.py                   # Database models
├── ethiopian_utils.py          # Ethiopian calendar conversion utilities
├── requirements.txt            # Python dependencies
├── run.bat                     # Windows startup script
├── index.html                  # HR Dashboard
├── login.html                  # Login page
├── owner_dashboard.html        # Owner metrics dashboard
├── attendance_kiosk.html       # Attendance check-in/out kiosk
├── public.html                 # Public information page
├── finance_dashboard.html      # Finance dashboard
├── style.css                   # Global styles
├── utils.js                    # JavaScript utilities
├── employee_import_template.csv # CSV import template
├── ETHIOPIAN_CALENDAR_GUIDE.md # Calendar conversion guide
└── CLEANUP_SUMMARY.txt         # Migration notes
```

## Usage Guide

### Employee Management
1. Navigate to **Employee List** tab
2. Use search and filters to find employees
3. Click **Add Employee** to create new records
4. Use **Edit**, **View**, **Suspend**, **Reactivate**, or **Archive** buttons for actions
5. Toggle calendar display using the button in the header

### Bulk Import
1. Prepare Excel/CSV file with required columns:
   - `employee_number`, `full_name`, `gender`, `age`, `position`
   - `employment_date_eth` (YYYY-MM-DD format)
   - `salary`
2. Click **Import CSV/Excel** button
3. Select your file
4. Review import results

### Attendance Kiosk
1. Open `http://localhost:5000/attendance_kiosk.html`
2. Enter employee number
3. Click **Check In** or **Check Out**
4. System records timestamp and validates actions

### Leave Management
1. Navigate to **Leave Management** tab
2. View automatically calculated leave balances
3. Click **Add Used Days** to record leave usage
4. System prevents negative balances

## Database Schema

### Main Tables
- **users**: System users with roles (hr/owner)
- **employees**: Employee master data with all fields
- **attendance_logs**: Daily check-in/out records
- **leave_used_log**: Leave usage history
- **contact_messages**: Public contact form submissions
- **audit_log**: System change tracking

### Key Calculations
- **Age**: Dynamically calculated from `birth_date`
- **Retirement Date**: `birth_date + 60 years`
- **Leave Balance**: Based on employment duration, suspensions, and usage

## Ethiopian Calendar Support

The system supports both Ethiopian and Gregorian calendars:
- **Storage**: All dates stored in Gregorian format (database standard)
- **Input**: Backend accepts Ethiopian dates and converts automatically
- **Output**: API returns both Gregorian and Ethiopian dates
- **Display**: Frontend toggle switches display format (no data change)

See `ETHIOPIAN_CALENDAR_GUIDE.md` for conversion details.

## API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `GET /api/current-user` - Get current user info

### Employees
- `GET /api/employees` - List all employees (with filters)
- `POST /api/employees` - Create new employee
- `PUT /api/employees/<id>` - Update employee
- `POST /api/employees/<id>/suspend` - Suspend employee
- `POST /api/employees/<id>/reactivate` - Reactivate employee
- `POST /api/employees/<id>/archive` - Archive employee
- `PUT /api/employees/<id>/health` - Update health status
- `POST /api/employees/import` - Bulk CSV/Excel import

### Attendance
- `POST /api/attendance/kiosk` - Kiosk check-in/out (public)
- `GET /api/attendance/logs` - Get attendance records

### Leave Management
- `GET /api/leave/balances` - Get all leave balances
- `POST /api/leave/used` - Add used leave days
- `GET /api/leave/used/history` - Get leave usage history

### Other
- `GET /api/owner/metrics` - Dashboard metrics
- `GET /api/audit` - Audit log entries
- `GET /api/messages` - Contact messages
- `POST /api/contact` - Submit contact message (public)

## Technologies Used

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Calendar**: ethiopian-date, convertdate
- **Data Processing**: pandas, openpyxl
- **Security**: werkzeug password hashing, CSRF protection

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is private and proprietary to Victory Water & Happy Juice.

## Support

For issues and questions, please contact the development team.

---

**Developed by**: Victory Water & Happy Juice IT Team  
**Last Updated**: June 6, 2026
