# app/models.py
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from app import get_db
import sqlite3
from datetime import datetime

class User:
    @staticmethod
    def create(name, email, password, role):
        """Create a new user in the database"""
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Hash the password
            hashed_password = generate_password_hash(password)
            print(f"Creating user: {email} with role: {role}")
            
            # Insert user
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                (name, email, hashed_password, role)
            )
            db.commit()
            
            user_id = cursor.lastrowid
            print(f"User created with ID: {user_id}")
            
            cursor.close()
            db.close()
            return user_id
            
        except sqlite3.IntegrityError:
            print(f"Email already exists: {email}")
            raise Exception("Email already exists")
        except Exception as e:
            print(f"Error creating user: {e}")
            raise
    
    @staticmethod
    def get_by_email(email):
        """Get a user by email"""
        try:
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            
            cursor.close()
            db.close()
            
            if row:
                user = {
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'password': row[3],
                    'role': row[4],
                    'created_at': row[5]
                }
                print(f"Found user: {user['email']} (Role: {user['role']})")
                return user
            else:
                print(f"No user found with email: {email}")
                return None
                
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    @staticmethod
    def get_by_id(user_id):
        """Get a user by ID"""
        try:
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            
            cursor.close()
            db.close()
            
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'password': row[3],
                    'role': row[4],
                    'created_at': row[5]
                }
            return None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        """Verify a password"""
        try:
            result = check_password_hash(stored_password, provided_password)
            print(f"Password verification result: {result}")
            return result
        except Exception as e:
            print(f"Error verifying password: {e}")
            return False

class Patient:
    @staticmethod
    def create(user_id, age, gender, phone):
        """Create a patient profile"""
        try:
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute(
                "INSERT INTO patients (user_id, age, gender, phone) VALUES (?, ?, ?, ?)",
                (user_id, age, gender, phone)
            )
            db.commit()
            
            patient_id = cursor.lastrowid
            print(f"Patient profile created for user {user_id}")
            
            cursor.close()
            db.close()
            return patient_id
            
        except Exception as e:
            print(f"Error creating patient: {e}")
            raise
    
    @staticmethod
    def get_by_user_id(user_id):
        """Get patient by user ID"""
        try:
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute("SELECT * FROM patients WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            cursor.close()
            db.close()
            
            if row:
                return {
                    'id': row[0],
                    'user_id': row[1],
                    'age': row[2],
                    'gender': row[3],
                    'phone': row[4]
                }
            return None
        except Exception as e:
            print(f"Error getting patient: {e}")
            return None
    
    @staticmethod
    def get_all_doctors():
        """Get all doctors"""
        try:
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT d.id, u.name, d.specialization 
                FROM doctors d 
                JOIN users u ON d.user_id = u.id
            """)
            rows = cursor.fetchall()
            
            doctors = []
            for row in rows:
                doctors.append({
                    'id': row[0],
                    'name': row[1],
                    'specialization': row[2]
                })
            
            cursor.close()
            db.close()
            return doctors
            
        except Exception as e:
            print(f"Error getting doctors: {e}")
            return []

class Doctor:
    @staticmethod
    def create(user_id, specialization):
        """Create a doctor profile"""
        try:
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute(
                "INSERT INTO doctors (user_id, specialization) VALUES (?, ?)",
                (user_id, specialization)
            )
            db.commit()
            
            doctor_id = cursor.lastrowid
            print(f"Doctor profile created for user {user_id}")
            
            cursor.close()
            db.close()
            return doctor_id
            
        except Exception as e:
            print(f"Error creating doctor: {e}")
            raise
    
    @staticmethod
    def get_by_user_id(user_id):
        """Get doctor by user ID"""
        try:
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute("SELECT * FROM doctors WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            cursor.close()
            db.close()
            
            if row:
                return {
                    'id': row[0],
                    'user_id': row[1],
                    'specialization': row[2]
                }
            return None
        except Exception as e:
            print(f"Error getting doctor: {e}")
            return None
    
    @staticmethod
    def get_pending_appointments(doctor_id):
        """Get pending appointments for a doctor"""
        try:
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT a.*, p.age, p.gender, p.phone, u.name as patient_name
                FROM appointments a
                JOIN patients p ON a.patient_id = p.id
                JOIN users u ON p.user_id = u.id
                WHERE a.doctor_id = ? AND a.status = 'Pending'
                ORDER BY a.appointment_date, a.time_slot
            """, (doctor_id,))
            
            rows = cursor.fetchall()
            appointments = []
            for row in rows:
                appointments.append({
                    'id': row[0],
                    'patient_id': row[1],
                    'doctor_id': row[2],
                    'appointment_date': row[3],
                    'time_slot': row[4],
                    'symptoms': row[5],
                    'status': row[6],
                    'rejection_reason': row[7],
                    'created_at': row[8],
                    'age': row[9],
                    'gender': row[10],
                    'phone': row[11],
                    'patient_name': row[12]
                })
            
            cursor.close()
            db.close()
            return appointments
            
        except Exception as e:
            print(f"Error getting pending appointments: {e}")
            return []
    
    @staticmethod
    def get_todays_appointments(doctor_id):
        """Get today's appointments for a doctor"""
        try:
            db = get_db()
            cursor = db.cursor()
            today = datetime.now().date()
            
            cursor.execute("""
                SELECT a.*, p.age, p.gender, u.name as patient_name
                FROM appointments a
                JOIN patients p ON a.patient_id = p.id
                JOIN users u ON p.user_id = u.id
                WHERE a.doctor_id = ? AND a.appointment_date = ? AND a.status = 'Approved'
                ORDER BY a.time_slot
            """, (doctor_id, today))
            
            rows = cursor.fetchall()
            appointments = []
            for row in rows:
                appointments.append({
                    'id': row[0],
                    'patient_id': row[1],
                    'doctor_id': row[2],
                    'appointment_date': row[3],
                    'time_slot': row[4],
                    'symptoms': row[5],
                    'status': row[6],
                    'rejection_reason': row[7],
                    'created_at': row[8],
                    'age': row[9],
                    'gender': row[10],
                    'patient_name': row[11]
                })
            
            cursor.close()
            db.close()
            return appointments
            
        except Exception as e:
            print(f"Error getting today's appointments: {e}")
            return []
    
    @staticmethod
    def get_appointments_by_date(doctor_id, date):
        """Get appointments by date for a doctor"""
        try:
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT a.*, p.age, p.gender, u.name as patient_name, p.phone
                FROM appointments a
                JOIN patients p ON a.patient_id = p.id
                JOIN users u ON p.user_id = u.id
                WHERE a.doctor_id = ? AND a.appointment_date = ? AND a.status = 'Approved'
                ORDER BY a.time_slot
            """, (doctor_id, date))
            
            rows = cursor.fetchall()
            appointments = []
            for row in rows:
                appointments.append({
                    'id': row[0],
                    'patient_id': row[1],
                    'doctor_id': row[2],
                    'appointment_date': row[3],
                    'time_slot': row[4],
                    'symptoms': row[5],
                    'status': row[6],
                    'rejection_reason': row[7],
                    'created_at': row[8],
                    'age': row[9],
                    'gender': row[10],
                    'patient_name': row[11],
                    'phone': row[12]
                })
            
            cursor.close()
            db.close()
            return appointments
            
        except Exception as e:
            print(f"Error getting appointments by date: {e}")
            return []

class Appointment:
    @staticmethod
    def create(patient_id, doctor_id, appointment_date, time_slot, symptoms):
        """Create a new appointment"""
        try:
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute("""
                INSERT INTO appointments 
                (patient_id, doctor_id, appointment_date, time_slot, symptoms) 
                VALUES (?, ?, ?, ?, ?)
            """, (patient_id, doctor_id, appointment_date, time_slot, symptoms))
            
            db.commit()
            appointment_id = cursor.lastrowid
            print(f"Appointment created with ID: {appointment_id}")
            
            cursor.close()
            db.close()
            return True, appointment_id
            
        except sqlite3.IntegrityError:
            print("Slot already booked")
            return False, "This time slot is already booked"
        except Exception as e:
            print(f"Error creating appointment: {e}")
            return False, str(e)
    
    @staticmethod
    def get_patient_appointments(patient_id):
        """Get all appointments for a patient"""
        try:
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT a.*, u.name as doctor_name, d.specialization
                FROM appointments a
                JOIN doctors d ON a.doctor_id = d.id
                JOIN users u ON d.user_id = u.id
                WHERE a.patient_id = ?
                ORDER BY a.appointment_date DESC, a.time_slot DESC
            """, (patient_id,))
            
            rows = cursor.fetchall()
            appointments = []
            for row in rows:
                appointments.append({
                    'id': row[0],
                    'patient_id': row[1],
                    'doctor_id': row[2],
                    'appointment_date': row[3],
                    'time_slot': row[4],
                    'symptoms': row[5],
                    'status': row[6],
                    'rejection_reason': row[7],
                    'created_at': row[8],
                    'doctor_name': row[9],
                    'specialization': row[10]
                })
            
            cursor.close()
            db.close()
            return appointments
            
        except Exception as e:
            print(f"Error getting patient appointments: {e}")
            return []
    
    @staticmethod
    def update_status(appointment_id, status, rejection_reason=None):
        """Update appointment status"""
        try:
            db = get_db()
            cursor = db.cursor()
            
            if status == 'Rejected' and rejection_reason:
                cursor.execute(
                    "UPDATE appointments SET status = ?, rejection_reason = ? WHERE id = ?",
                    (status, rejection_reason, appointment_id)
                )
            else:
                cursor.execute(
                    "UPDATE appointments SET status = ? WHERE id = ?",
                    (status, appointment_id)
                )
            
            db.commit()
            cursor.close()
            db.close()
            return True
            
        except Exception as e:
            print(f"Error updating appointment: {e}")
            return False
    
    @staticmethod
    def check_slot_available(doctor_id, appointment_date, time_slot):
        """Check if a time slot is available"""
        try:
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute(
                """SELECT id FROM appointments 
                   WHERE doctor_id = ? AND appointment_date = ? AND time_slot = ?""",
                (doctor_id, appointment_date, time_slot)
            )
            existing = cursor.fetchone()
            
            cursor.close()
            db.close()
            return existing is None
            
        except Exception as e:
            print(f"Error checking slot availability: {e}")
            return False
    
    @staticmethod
    def check_patient_duplicate(patient_id, doctor_id, appointment_date, time_slot):
        """Check if patient already booked this slot"""
        try:
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT id FROM appointments 
                WHERE patient_id = ? AND doctor_id = ? 
                AND appointment_date = ? AND time_slot = ?
            """, (patient_id, doctor_id, appointment_date, time_slot))
            
            existing = cursor.fetchone()
            
            cursor.close()
            db.close()
            return existing is not None
            
        except Exception as e:
            print(f"Error checking duplicate: {e}")
            return False