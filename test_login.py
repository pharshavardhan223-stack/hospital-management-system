# test_login.py
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

print("=" * 60)
print("LOGIN DEBUGGING TOOL")
print("=" * 60)

# Connect to database
db_path = 'hospital.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get all users
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

print(f"\n📊 Users in database: {len(users)}")
print("-" * 60)

for user in users:
    print(f"\n👤 User: {user['name']}")
    print(f"   Email: {user['email']}")
    print(f"   Role: {user['role']}")
    print(f"   Password hash: {user['password'][:50]}...")
    
    # Test with common passwords
    test_passwords = ['password123', 'doctor123', 'patient123', 'admin123']
    for test_pw in test_passwords:
        result = check_password_hash(user['password'], test_pw)
        if result:
            print(f"   ✅ Password '{test_pw}' WORKS!")
            break
    else:
        print(f"   ❌ No common password works")

print("\n" + "=" * 60)
print("🔧 MANUAL TEST:")
print("=" * 60)
print("\nEnter an email and password to test:")
test_email = input("Email: ").strip()
test_password = input("Password: ").strip()

cursor.execute("SELECT * FROM users WHERE email = ?", (test_email,))
user = cursor.fetchone()

if user:
    print(f"\n✓ User found: {user['name']}")
    if check_password_hash(user['password'], test_password):
        print("✅ LOGIN SUCCESSFUL - Password matches!")
    else:
        print("❌ LOGIN FAILED - Password does not match")
        print(f"   Stored hash: {user['password'][:50]}...")
else:
    print(f"❌ No user found with email: {test_email}")

conn.close()