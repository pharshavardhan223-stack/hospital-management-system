# check_doctor.py
import sqlite3
from werkzeug.security import check_password_hash

print("=" * 60)
print("DOCTOR REGISTRATION CHECKER")
print("=" * 60)

# Connect to database
conn = sqlite3.connect('hospital.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check all users
print("\n📊 ALL USERS IN DATABASE:")
print("-" * 40)
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

for user in users:
    print(f"\nID: {user['id']}")
    print(f"Name: {user['name']}")
    print(f"Email: {user['email']}")
    print(f"Role: {user['role']}")
    print(f"Created: {user['created_at']}")

# Check doctors table
print("\n" + "=" * 60)
print("📊 DOCTORS TABLE:")
print("-" * 40)
cursor.execute("""
    SELECT d.*, u.name, u.email 
    FROM doctors d 
    JOIN users u ON d.user_id = u.id
""")
doctors = cursor.fetchall()

if doctors:
    for doctor in doctors:
        print(f"\nDoctor ID: {doctor['id']}")
        print(f"User ID: {doctor['user_id']}")
        print(f"Name: {doctor['name']}")
        print(f"Email: {doctor['email']}")
        print(f"Specialization: {doctor['specialization']}")
else:
    print("❌ No doctors found in doctors table!")

# Check for users with role='doctor' but missing in doctors table
print("\n" + "=" * 60)
print("🔍 CHECKING FOR INCOMPLETE DOCTOR REGISTRATIONS:")
print("-" * 40)
cursor.execute("""
    SELECT u.id, u.name, u.email 
    FROM users u 
    LEFT JOIN doctors d ON u.id = d.user_id 
    WHERE u.role = 'doctor' AND d.id IS NULL
""")
incomplete = cursor.fetchall()

if incomplete:
    for user in incomplete:
        print(f"❌ User {user['name']} ({user['email']}) has role 'doctor' but no doctor profile!")
else:
    print("✓ All doctors have complete profiles")

conn.close()
print("\n" + "=" * 60)