# setup_db.py
import sqlite3
import os
from werkzeug.security import generate_password_hash

print("=" * 50)
print("HOSPITAL MANAGEMENT SYSTEM - DATABASE SETUP")
print("=" * 50)

# Database path
db_path = 'hospital.db'

# Remove existing database if it exists
if os.path.exists(db_path):
    os.remove(db_path)
    print("✓ Removed old database")
else:
    print("✓ No existing database found")

# Create new database connection
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
print("✓ Created new database")

# Create users table
print("\n📁 Creating tables...")
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('patient', 'doctor')) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print("  ✓ Users table created")

# Create patients table
cursor.execute('''
    CREATE TABLE patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')) NOT NULL,
        phone TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
''')
print("  ✓ Patients table created")

# Create doctors table
cursor.execute('''
    CREATE TABLE doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        specialization TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
''')
print("  ✓ Doctors table created")

# Create appointments table
cursor.execute('''
    CREATE TABLE appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        appointment_date DATE NOT NULL,
        time_slot TEXT NOT NULL,
        symptoms TEXT,
        status TEXT CHECK(status IN ('Pending', 'Approved', 'Rejected')) DEFAULT 'Pending',
        rejection_reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE,
        FOREIGN KEY (doctor_id) REFERENCES doctors (id) ON DELETE CASCADE,
        UNIQUE(doctor_id, appointment_date, time_slot)
    )
''')
print("  ✓ Appointments table created")

# Create indexes
cursor.execute('CREATE INDEX idx_appointments_date ON appointments(appointment_date)')
cursor.execute('CREATE INDEX idx_appointments_status ON appointments(status)')
cursor.execute('CREATE INDEX idx_appointments_doctor_date ON appointments(doctor_id, appointment_date)')
print("  ✓ Indexes created")

# Commit the table creation
conn.commit()
print("\n✅ Database schema created successfully!")

# Create test accounts
print("\n👤 Creating test accounts...")

# Test password
test_password = "password123"
hashed_password = generate_password_hash(test_password)
print(f"  Using password: '{test_password}'")
print(f"  Hash generated: {hashed_password[:30]}...")

# Create doctor account
cursor.execute(
    "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
    ('Dr. John Smith', 'doctor@test.com', hashed_password, 'doctor')
)
doctor_user_id = cursor.lastrowid
print(f"  ✓ Doctor user created with ID: {doctor_user_id}")

cursor.execute(
    "INSERT INTO doctors (user_id, specialization) VALUES (?, ?)",
    (doctor_user_id, 'Cardiology')
)
print("  ✓ Doctor profile created")

# Create patient account
cursor.execute(
    "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
    ('Jane Patient', 'patient@test.com', hashed_password, 'patient')
)
patient_user_id = cursor.lastrowid
print(f"  ✓ Patient user created with ID: {patient_user_id}")

cursor.execute(
    "INSERT INTO patients (user_id, age, gender, phone) VALUES (?, ?, ?, ?)",
    (patient_user_id, 28, 'Female', '9876543210')
)
print("  ✓ Patient profile created")

# Commit the test accounts
conn.commit()

print("\n" + "=" * 50)
print("✅ TEST ACCOUNTS CREATED SUCCESSFULLY!")
print("=" * 50)
print("📧 DOCTOR LOGIN:")
print("   Email: doctor@test.com")
print(f"   Password: {test_password}")
print()
print("📧 PATIENT LOGIN:")
print("   Email: patient@test.com")
print(f"   Password: {test_password}")
print("=" * 50)

# Verify the accounts were created correctly
print("\n🔍 Verifying database contents...")

cursor.execute("SELECT COUNT(*) as count FROM users")
user_count = cursor.fetchone()[0]
print(f"  ✓ Total users in database: {user_count}")

cursor.execute("SELECT COUNT(*) as count FROM doctors")
doctor_count = cursor.fetchone()[0]
print(f"  ✓ Total doctors in database: {doctor_count}")

cursor.execute("SELECT COUNT(*) as count FROM patients")
patient_count = cursor.fetchone()[0]
print(f"  ✓ Total patients in database: {patient_count}")

# Test password verification
print("\n🔐 Testing password verification...")
cursor.execute("SELECT email, password FROM users")
users = cursor.fetchall()
for user in users:
    from werkzeug.security import check_password_hash
    result = check_password_hash(user[1], test_password)
    status = "✓ WORKS" if result else "✗ FAILS"
    print(f"  {status} - {user[0]}: Password verification {result}")

conn.close()
print("\n" + "=" * 50)
print("✅ DATABASE SETUP COMPLETE!")
print("=" * 50)