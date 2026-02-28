# check_appointment.py
import sqlite3
from datetime import datetime

print("=" * 60)
print("APPOINTMENT SYSTEM CHECK")
print("=" * 60)

# Check database
conn = sqlite3.connect('hospital.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check tables
print("\n📊 CHECKING DATABASE TABLES:")
tables = ['users', 'patients', 'doctors', 'appointments']
for table in tables:
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
    if cursor.fetchone():
        print(f"  ✓ {table} table exists")
    else:
        print(f"  ❌ {table} table missing!")

# Check doctors
print("\n👨‍⚕️ DOCTORS IN SYSTEM:")
cursor.execute("""
    SELECT d.id, u.name, d.specialization 
    FROM doctors d 
    JOIN users u ON d.user_id = u.id
""")
doctors = cursor.fetchall()
if doctors:
    for doc in doctors:
        print(f"  ID: {doc['id']}, Dr. {doc['name']} - {doc['specialization']}")
else:
    print("  ❌ No doctors found!")

# Check patients
print("\n👤 PATIENTS IN SYSTEM:")
cursor.execute("""
    SELECT p.id, u.name, u.email 
    FROM patients p 
    JOIN users u ON p.user_id = u.id
""")
patients = cursor.fetchall()
if patients:
    for pat in patients:
        print(f"  ID: {pat['id']}, {pat['name']} - {pat['email']}")
else:
    print("  ❌ No patients found!")

# Check today's date format
print(f"\n📅 Today's date: {datetime.now().date()}")
print(f"  Format example: {datetime.now().strftime('%Y-%m-%d')}")

conn.close()
print("\n" + "=" * 60)