# test_doctor_registration.py
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import time

print("=" * 60)
print("DOCTOR REGISTRATION TEST")
print("=" * 60)

def test_register_doctor(name, email, password, specialization):
    """Test doctor registration directly"""
    try:
        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()
        
        print(f"\n📝 Testing registration for: {email}")
        
        # Check if email exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            print("❌ Email already exists")
            return False
        
        # Create user
        hashed = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (name, email, hashed, 'doctor')
        )
        user_id = cursor.lastrowid
        print(f"✓ User created with ID: {user_id}")
        
        # Create doctor profile
        cursor.execute(
            "INSERT INTO doctors (user_id, specialization) VALUES (?, ?)",
            (user_id, specialization)
        )
        doctor_id = cursor.lastrowid
        print(f"✓ Doctor profile created with ID: {doctor_id}")
        
        conn.commit()
        
        # Verify
        cursor.execute("""
            SELECT u.*, d.specialization 
            FROM users u 
            JOIN doctors d ON u.id = d.user_id 
            WHERE u.id = ?
        """, (user_id,))
        result = cursor.fetchone()
        
        if result:
            print(f"✓ Verification successful:")
            print(f"  Name: {result[1]}")
            print(f"  Email: {result[2]}")
            print(f"  Role: {result[4]}")
            print(f"  Specialization: {result[7]}")
            
            # Test login
            if check_password_hash(result[3], password):
                print(f"✓ Password verification works!")
            else:
                print(f"❌ Password verification failed!")
        else:
            print(f"❌ Verification failed - doctor profile not linked")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# Test with unique email using timestamp
timestamp = int(time.time())
test_email = f"dr.test{timestamp}@hospital.com"

test_register_doctor(
    name="Dr. Test Doctor",
    email=test_email,
    password="doctor123",
    specialization="Cardiology"
)

print("\n" + "=" * 60)
print("\nNow try registering through the web interface with:")
print(f"Email: {test_email}")
print("Password: doctor123")
print("Specialization: Cardiology")
print("=" * 60)