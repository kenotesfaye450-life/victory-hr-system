"""
Quick diagnostic script to test database and server connections
"""
import sys

print("=" * 60)
print("VICTORY HR SYSTEM - CONNECTION DIAGNOSTICS")
print("=" * 60)

# Test 1: Check imports
print("\n[1/5] Testing Python imports...")
try:
    from flask import Flask
    from models import db, Employee
    from sqlalchemy import text
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Test 2: Create Flask app
print("\n[2/5] Testing Flask app initialization...")
try:
    from app import app
    print("✓ Flask app created successfully")
except Exception as e:
    print(f"✗ Flask app error: {e}")
    sys.exit(1)

# Test 3: Test database connection
print("\n[3/5] Testing PostgreSQL connection...")
try:
    with app.app_context():
        result = db.session.execute(text('SELECT 1')).fetchone()
        print(f"✓ Database connected: {result}")
except Exception as e:
    print(f"✗ Database connection error: {e}")
    print("\nPossible solutions:")
    print("  1. Start PostgreSQL service")
    print("  2. Check database 'victory_hr' exists")
    print("  3. Verify password in app.py connection string")
    sys.exit(1)

# Test 4: Check if tables exist
print("\n[4/5] Testing database tables...")
try:
    with app.app_context():
        count = Employee.query.count()
        print(f"✓ Tables exist. Found {count} employees in database")
except Exception as e:
    print(f"✗ Table error: {e}")
    print("\nRun: python -c \"from app import app, init_db; init_db()\"")
    sys.exit(1)

# Test 5: Test API endpoint
print("\n[5/5] Testing API response...")
try:
    with app.app_context():
        employees = Employee.query.limit(5).all()
        if employees:
            print(f"✓ Can query employees. Sample: {employees[0].full_name}")
        else:
            print("⚠ Database is empty (no employees found)")
except Exception as e:
    print(f"✗ Query error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL DIAGNOSTICS PASSED!")
print("=" * 60)
print("\nYour system is ready. Start the server with:")
print("  python app.py")
print("\nThen open in browser:")
print("  http://127.0.0.1:5000")
print("=" * 60)
