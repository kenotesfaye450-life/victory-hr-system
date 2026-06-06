"""
System Optimization & Performance Check
"""
import os
import sys

print("=" * 60)
print("VICTORY HR SYSTEM - OPTIMIZATION CHECK")
print("=" * 60)

checks = {
    "passed": [],
    "warnings": [],
    "failed": []
}

# Check 1: File sizes
print("\n[1/8] Checking file sizes...")
files_to_check = {
    'index.html': 150000,  # 150KB max recommended
    'app.py': 100000,      # 100KB max recommended
    'style.css': 50000,    # 50KB max recommended
    'utils.js': 30000      # 30KB max recommended
}

for filename, max_size in files_to_check.items():
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        if size < max_size:
            checks["passed"].append(f"{filename}: {size:,} bytes (✓)")
        else:
            checks["warnings"].append(f"{filename}: {size:,} bytes (large, consider splitting)")
    else:
        checks["failed"].append(f"{filename}: NOT FOUND")

# Check 2: Required files exist
print("\n[2/8] Checking required files...")
required_files = [
    'app.py', 'models.py', 'ethiopian_utils.py', 'requirements.txt',
    'index.html', 'login.html', 'attendance_kiosk.html',
    'style.css', 'utils.js', 'README.md'
]

for filename in required_files:
    if os.path.exists(filename):
        checks["passed"].append(f"✓ {filename}")
    else:
        checks["failed"].append(f"✗ {filename} MISSING")

# Check 3: Temporary files cleanup
print("\n[3/8] Checking for temporary files...")
temp_patterns = ['*.pyc', '__pycache__', '*.log', '.DS_Store', 'Thumbs.db']
temp_found = []

for root, dirs, files in os.walk('.'):
    if '__pycache__' in dirs:
        temp_found.append('__pycache__ folder')
    for file in files:
        if file.endswith('.pyc'):
            temp_found.append(file)

if temp_found:
    checks["warnings"].append(f"Temporary files found: {len(temp_found)} (can be cleaned)")
else:
    checks["passed"].append("✓ No temporary files")

# Check 4: Documentation completeness
print("\n[4/8] Checking documentation...")
docs = [
    'README.md', 
    'SYSTEM_HEALTH_CHECK.md',
    'MIGRATION_INSTRUCTIONS.txt',
    'ALPHABETICAL_RANK_SUMMARY.txt'
]

doc_count = sum(1 for doc in docs if os.path.exists(doc))
if doc_count == len(docs):
    checks["passed"].append(f"✓ All {len(docs)} documentation files present")
else:
    checks["warnings"].append(f"Missing {len(docs) - doc_count} documentation files")

# Check 5: Git repository status
print("\n[5/8] Checking Git status...")
if os.path.exists('.git'):
    checks["passed"].append("✓ Git repository initialized")
else:
    checks["warnings"].append("Git not initialized (optional)")

# Check 6: Database migration files
print("\n[6/8] Checking migration files...")
if os.path.exists('fix_suspension_days.sql'):
    checks["warnings"].append("⚠ fix_suspension_days.sql present - needs to be run on database")
else:
    checks["passed"].append("✓ No pending migrations")

# Check 7: Security checks
print("\n[7/8] Checking security configuration...")
if os.path.exists('app.py'):
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'SECRET_KEY' in content:
            if 'victory-water-happy-juice-secret-key' in content:
                checks["warnings"].append("⚠ Using default SECRET_KEY (change for production)")
            else:
                checks["passed"].append("✓ Custom SECRET_KEY set")
        else:
            checks["failed"].append("✗ No SECRET_KEY found in app.py")

# Check 8: Performance optimizations
print("\n[8/8] Checking performance optimizations...")
optimizations = []

if os.path.exists('index.html'):
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'localeCompare' in content:
            optimizations.append("✓ Alphabetical sorting optimized")
        if 'localStorage' in content:
            optimizations.append("✓ Client-side caching enabled")
        if 'forEach((emp, index)' in content:
            optimizations.append("✓ Array indexing for rank")

if optimizations:
    checks["passed"].extend(optimizations)
else:
    checks["warnings"].append("No specific optimizations detected")

# Print summary
print("\n" + "=" * 60)
print("OPTIMIZATION REPORT SUMMARY")
print("=" * 60)

print(f"\n✅ PASSED: {len(checks['passed'])}")
for item in checks['passed'][:5]:  # Show first 5
    print(f"   {item}")
if len(checks['passed']) > 5:
    print(f"   ... and {len(checks['passed']) - 5} more")

if checks['warnings']:
    print(f"\n⚠️  WARNINGS: {len(checks['warnings'])}")
    for item in checks['warnings']:
        print(f"   {item}")

if checks['failed']:
    print(f"\n❌ FAILED: {len(checks['failed'])}")
    for item in checks['failed']:
        print(f"   {item}")

# Overall score
total = len(checks['passed']) + len(checks['warnings']) + len(checks['failed'])
score = (len(checks['passed']) / total * 100) if total > 0 else 0

print("\n" + "=" * 60)
print(f"OVERALL SCORE: {score:.1f}%")

if score >= 90:
    status = "✅ EXCELLENT - System is highly optimized"
elif score >= 75:
    status = "✅ GOOD - Minor optimizations recommended"
elif score >= 60:
    status = "⚠️  FAIR - Several optimizations needed"
else:
    status = "❌ POOR - Significant issues need attention"

print(status)
print("=" * 60)

# Recommendations
print("\n📋 QUICK RECOMMENDATIONS:")
if checks['warnings']:
    print("\n1. Address warnings listed above")
if 'fix_suspension_days.sql' in str(checks['warnings']):
    print("2. Run SQL migration: fix_suspension_days.sql")
if 'SECRET_KEY' in str(checks['warnings']):
    print("3. Change SECRET_KEY in app.py for production")
if temp_found:
    print("4. Clean temporary files with: python -m py_compile --clean")

print("\n5. Run full diagnostics: python test_connection.py")
print("6. Start server: python app.py")
print("7. Test in browser: http://127.0.0.1:5000")

print("\n" + "=" * 60)
