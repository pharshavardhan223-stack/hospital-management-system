from flask import session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app import get_db
from datetime import datetime

class User:
    @staticmethod
    def create(name, email, password, role):
        db = get_db()
        cursor = db.cursor()
        from werkzeug.security import generate_password_hash
        hashed_password = generate_password_hash(password)
        print(f"Creating user: {email} with password hash")  # Debug
        
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (name, email, hashed_password, role)
        )
        db.commit()
        user_id = cursor.lastrowid
        cursor.close()
        db.close()
        return user_id
    
    @staticmethod
    def get_by_email(email):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        
        if user:
            # Convert sqlite3.Row to dictionary
            user_dict = {
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'password': user[3],
                'role': user[4],
                'created_at': user[5]
            }
            return user_dict
        return None
    
    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        
        if user:
            user_dict = {
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'password': user[3],
                'role': user[4],
                'created_at': user[5]
            }
            return user_dict
        return None
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        from werkzeug.security import check_password_hash
        return check_password_hash(stored_password, provided_password)

class Patient:
    @staticmethod
    def create(user_id, age, gender, phone):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO patients (user_id, age, gender, phone) VALUES (?, ?, ?, ?)",
            (user_id, age, gender, phone)
        )
        db.commit()
        patient_id = cursor.lastrowid
        cursor.close()
        db.close()
        return patient_id
    
    @staticmethod
    def get_by_user_id(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM patients WHERE user_id = ?", (user_id,))
        patient = cursor.fetchone()
        cursor.close()
        db.close()
        
        if patient:
            patient_dict = {
                'id': patient[0],
                'user_id': patient[1],
                'age': patient[2],
                'gender': patient[3],
                'phone': patient[4]
            }
            return patient_dict
        return None
    
    @staticmethod
    def get_all_doctors():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT d.id, u.name, d.specialization 
            FROM doctors d 
            JOIN users u ON d.user_id = u.id
        """)
        doctors = cursor.fetchall()
        result = []
        for doc in doctors:
            result.append({
                'id': doc[0],
                'name': doc[1],
                'specialization': doc[2]
            })
        cursor.close()
        db.close()
        return result

class Doctor:
    @staticmethod
    def create(user_id, specialization):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO doctors (user_id, specialization) VALUES (?, ?)",
            (user_id, specialization)
        )
        db.commit()
        doctor_id = cursor.lastrowid
        cursor.close()
        db.close()
        return doctor_id
    
    @staticmethod
    def get_by_user_id(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM doctors WHERE user_id = ?", (user_id,))
        doctor = cursor.fetchone()
        cursor.close()
        db.close()
        
        if doctor:
            doctor_dict = {
                'id': doctor[0],
                'user_id': doctor[1],
                'specialization': doctor[2]
            }
            return doctor_dict
        return None
    
    @staticmethod
    def get_pending_appointments(doctor_id):
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
        appointments = cursor.fetchall()
        result = []
        for apt in appointments:
            result.append({
                'id': apt[0],
                'patient_id': apt[1],
                'doctor_id': apt[2],
                'appointment_date': apt[3],
                'time_slot': apt[4],
                'symptoms': apt[5],
                'status': apt[6],
                'rejection_reason': apt[7],
                'created_at': apt[8],
                'age': apt[9],
                'gender': apt[10],
                'phone': apt[11],
                'patient_name': apt[12]
            })
        cursor.close()
        db.close()
        return result
    
    @staticmethod
    def get_todays_appointments(doctor_id):
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
        appointments = cursor.fetchall()
        result = []
        for apt in appointments:
            result.append({
                'id': apt[0],
                'patient_id': apt[1],
                'doctor_id': apt[2],
                'appointment_date': apt[3],
                'time_slot': apt[4],
                'symptoms': apt[5],
                'status': apt[6],
                'rejection_reason': apt[7],
                'created_at': apt[8],
                'age': apt[9],
                'gender': apt[10],
                'patient_name': apt[11]
            })
        cursor.close()
        db.close()
        return result
    
    @staticmethod
    def get_appointments_by_date(doctor_id, date):
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
        appointments = cursor.fetchall()
        result = []
        for apt in appointments:
            result.append({
                'id': apt[0],
                'patient_id': apt[1],
                'doctor_id': apt[2],
                'appointment_date': apt[3],
                'time_slot': apt[4],
                'symptoms': apt[5],
                'status': apt[6],
                'rejection_reason': apt[7],
                'created_at': apt[8],
                'age': apt[9],
                'gender': apt[10],
                'patient_name': apt[11],
                'phone': apt[12]
            })
        cursor.close()
        db.close()
        return result

class Appointment:
    @staticmethod
    def create(patient_id, doctor_id, appointment_date, time_slot, symptoms):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO appointments 
                (patient_id, doctor_id, appointment_date, time_slot, symptoms) 
                VALUES (?, ?, ?, ?, ?)
            """, (patient_id, doctor_id, appointment_date, time_slot, symptoms))
            db.commit()
            appointment_id = cursor.lastrowid
            cursor.close()
            db.close()
            return True, appointment_id
        except Exception as e:
            db.rollback()
            cursor.close()
            db.close()
            return False, str(e)
    
    @staticmethod
    def get_patient_appointments(patient_id):
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
        appointments = cursor.fetchall()
        result = []
        for apt in appointments:
            result.append({
                'id': apt[0],
                'patient_id': apt[1],
                'doctor_id': apt[2],
                'appointment_date': apt[3],
                'time_slot': apt[4],
                'symptoms': apt[5],
                'status': apt[6],
                'rejection_reason': apt[7],
                'created_at': apt[8],
                'doctor_name': apt[9],
                'specialization': apt[10]
            })
        cursor.close()
        db.close()
        return result
    
    @staticmethod
    def update_status(appointment_id, status, rejection_reason=None):
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
    
    @staticmethod
    def check_slot_available(doctor_id, appointment_date, time_slot):
        """Check if a specific time slot is available for booking"""
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
    
    @staticmethod
    def check_patient_duplicate(patient_id, doctor_id, appointment_date, time_slot):
        """Check if patient already booked this specific slot"""
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

# ===== CHAT SYSTEM MODELS =====
class Conversation:
    @staticmethod
    def create_table():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id INTEGER NOT NULL,
                patient_id INTEGER NOT NULL,
                appointment_id INTEGER,
                last_message TEXT,
                last_message_time TIMESTAMP,
                unread_doctor INTEGER DEFAULT 0,
                unread_patient INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (doctor_id) REFERENCES doctors (id) ON DELETE CASCADE,
                FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE,
                FOREIGN KEY (appointment_id) REFERENCES appointments (id) ON DELETE SET NULL,
                UNIQUE(doctor_id, patient_id, appointment_id)
            )
        ''')
        db.commit()
        cursor.close()
        db.close()
        print("✅ Conversations table created")

    @staticmethod
    def get_or_create(doctor_id, patient_id, appointment_id=None):
        db = get_db()
        cursor = db.cursor()
        
        # Check if conversation exists
        cursor.execute('''
            SELECT * FROM conversations 
            WHERE doctor_id = ? AND patient_id = ? 
            AND (appointment_id = ? OR (appointment_id IS NULL AND ? IS NULL))
        ''', (doctor_id, patient_id, appointment_id, appointment_id))
        
        conv = cursor.fetchone()
        
        if not conv:
            cursor.execute('''
                INSERT INTO conversations (doctor_id, patient_id, appointment_id)
                VALUES (?, ?, ?)
            ''', (doctor_id, patient_id, appointment_id))
            db.commit()
            conv_id = cursor.lastrowid
        else:
            conv_id = conv[0]
        
        cursor.close()
        db.close()
        return conv_id

    @staticmethod
    def get_for_doctor(doctor_id):
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT c.*, u.name as patient_name, p.age, p.gender, p.phone,
                   (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id AND sender_role = 'patient' AND is_read = 0) as unread
            FROM conversations c
            JOIN patients p ON c.patient_id = p.id
            JOIN users u ON p.user_id = u.id
            WHERE c.doctor_id = ? AND c.status = 'active'
            ORDER BY c.last_message_time DESC NULLS LAST
        ''', (doctor_id,))
        
        conversations = cursor.fetchall()
        result = []
        for conv in conversations:
            result.append({
                'id': conv[0],
                'doctor_id': conv[1],
                'patient_id': conv[2],
                'appointment_id': conv[3],
                'last_message': conv[4],
                'last_message_time': conv[5],
                'unread_doctor': conv[6],
                'unread_patient': conv[7],
                'status': conv[8],
                'created_at': conv[9],
                'patient_name': conv[10],
                'age': conv[11],
                'gender': conv[12],
                'phone': conv[13],
                'unread': conv[14]
            })
        cursor.close()
        db.close()
        return result

    @staticmethod
    def get_for_patient(patient_id):
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT c.*, u.name as doctor_name, d.specialization,
                   (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id AND sender_role = 'doctor' AND is_read = 0) as unread
            FROM conversations c
            JOIN doctors d ON c.doctor_id = d.id
            JOIN users u ON d.user_id = u.id
            WHERE c.patient_id = ? AND c.status = 'active'
            ORDER BY c.last_message_time DESC NULLS LAST
        ''', (patient_id,))
        
        conversations = cursor.fetchall()
        result = []
        for conv in conversations:
            result.append({
                'id': conv[0],
                'doctor_id': conv[1],
                'patient_id': conv[2],
                'appointment_id': conv[3],
                'last_message': conv[4],
                'last_message_time': conv[5],
                'unread_doctor': conv[6],
                'unread_patient': conv[7],
                'status': conv[8],
                'created_at': conv[9],
                'doctor_name': conv[10],
                'specialization': conv[11],
                'unread': conv[12]
            })
        cursor.close()
        db.close()
        return result

    @staticmethod
    def mark_read(conversation_id, role):
        db = get_db()
        cursor = db.cursor()
        
        if role == 'doctor':
            cursor.execute('UPDATE conversations SET unread_doctor = 0 WHERE id = ?', (conversation_id,))
        else:
            cursor.execute('UPDATE conversations SET unread_patient = 0 WHERE id = ?', (conversation_id,))
        
        db.commit()
        cursor.close()
        db.close()

class Message:
    @staticmethod
    def create_table():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                sender_id INTEGER NOT NULL,
                sender_role TEXT NOT NULL,
                message TEXT NOT NULL,
                attachment TEXT,
                is_read BOOLEAN DEFAULT 0,
                is_emergency BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
            )
        ''')
        db.commit()
        cursor.close()
        db.close()
        print("✅ Messages table created")

    @staticmethod
    def send(conversation_id, sender_id, sender_role, message, attachment=None, is_emergency=False):
        db = get_db()
        cursor = db.cursor()
        
        # Insert message
        cursor.execute('''
            INSERT INTO messages (conversation_id, sender_id, sender_role, message, attachment, is_emergency)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (conversation_id, sender_id, sender_role, message, attachment, is_emergency))
        
        # Update conversation last message
        cursor.execute('''
            UPDATE conversations 
            SET last_message = ?, last_message_time = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (message[:50] + '...' if len(message) > 50 else message, conversation_id))
        
        # Update unread count
        if sender_role == 'doctor':
            cursor.execute('UPDATE conversations SET unread_patient = unread_patient + 1 WHERE id = ?', (conversation_id,))
        else:
            cursor.execute('UPDATE conversations SET unread_doctor = unread_doctor + 1 WHERE id = ?', (conversation_id,))
        
        db.commit()
        message_id = cursor.lastrowid
        
        # Get created time
        cursor.execute('SELECT created_at FROM messages WHERE id = ?', (message_id,))
        created_at = cursor.fetchone()[0]
        
        cursor.close()
        db.close()
        
        return {
            'id': message_id,
            'time': created_at.split(' ')[1][:5] if ' ' in created_at else '00:00'
        }

    @staticmethod
    def get_for_conversation(conversation_id, limit=50):
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT * FROM messages 
            WHERE conversation_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (conversation_id, limit))
        
        messages = cursor.fetchall()
        result = []
        for msg in messages:
            result.append({
                'id': msg[0],
                'conversation_id': msg[1],
                'sender_id': msg[2],
                'sender_role': msg[3],
                'message': msg[4],
                'attachment': msg[5],
                'is_read': msg[6],
                'is_emergency': msg[7],
                'created_at': msg[8]
            })
        cursor.close()
        db.close()
        return result

    @staticmethod
    def mark_conversation_read(conversation_id, role):
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            UPDATE messages SET is_read = 1 
            WHERE conversation_id = ? AND sender_role != ?
        ''', (conversation_id, role))
        
        db.commit()
        cursor.close()
        db.close()

    @staticmethod
    def get_unread_count(user_id, role):
        db = get_db()
        cursor = db.cursor()
        
        if role == 'doctor':
            cursor.execute('''
                SELECT SUM(unread_doctor) FROM conversations 
                WHERE doctor_id = ? AND status = 'active'
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT SUM(unread_patient) FROM conversations 
                WHERE patient_id = ? AND status = 'active'
            ''', (user_id,))
        
        count = cursor.fetchone()[0] or 0
        cursor.close()
        db.close()
        return count