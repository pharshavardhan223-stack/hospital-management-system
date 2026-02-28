# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import User, Patient, Doctor
from app.utils import login_required
import traceback
import sqlite3

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            role = request.form.get('role', '')
            
            print("\n" + "="*60)
            print("NEW REGISTRATION ATTEMPT")
            print("="*60)
            print(f"Name: {name}")
            print(f"Email: {email}")
            print(f"Role: {role}")
            print(f"Password length: {len(password)}")
            
            # Basic validation
            if not all([name, email, password, role]):
                flash('All fields are required', 'danger')
                return redirect(url_for('auth.register'))
            
            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return redirect(url_for('auth.register'))
            
            if len(password) < 6:
                flash('Password must be at least 6 characters', 'danger')
                return redirect(url_for('auth.register'))
            
            # Check if user exists
            existing_user = User.get_by_email(email)
            if existing_user:
                flash('Email already registered', 'danger')
                return redirect(url_for('auth.register'))
            
            # Create user
            user_id = User.create(name, email, password, role)
            print(f"✓ User created with ID: {user_id}")
            
            # Create role-specific profile
            if role == 'patient':
                age = request.form.get('age')
                gender = request.form.get('gender')
                phone = request.form.get('phone')
                
                print(f"Patient details - Age: {age}, Gender: {gender}, Phone: {phone}")
                
                if not all([age, gender, phone]):
                    flash('Please fill all patient details', 'danger')
                    return redirect(url_for('auth.register'))
                
                patient_id = Patient.create(user_id, age, gender, phone)
                print(f"✓ Patient profile created with ID: {patient_id}")
                flash('Patient registration successful! Please login.', 'success')
                
            elif role == 'doctor':
                specialization = request.form.get('specialization', '').strip()
                
                print(f"Doctor specialization: {specialization}")
                
                if not specialization:
                    flash('Please enter your specialization', 'danger')
                    return redirect(url_for('auth.register'))
                
                doctor_id = Doctor.create(user_id, specialization)
                print(f"✓ Doctor profile created with ID: {doctor_id}")
                flash('Doctor registration successful! Please login.', 'success')
            
            print("="*60)
            print("REGISTRATION COMPLETED SUCCESSFULLY")
            print("="*60)
            
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            print(f"!!! ERROR IN REGISTRATION: {str(e)}")
            print(traceback.format_exc())
            flash(f'Registration failed: {str(e)}', 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        print("\n" + "="*60)
        print("LOGIN ATTEMPT")
        print("="*60)
        print(f"Email: {email}")
        print(f"Password length: {len(password)}")
        
        if not email or not password:
            flash('Please enter email and password', 'danger')
            return redirect(url_for('auth.login'))
        
        # Get user from database
        user = User.get_by_email(email)
        
        if user:
            print(f"✓ User found: {user['name']} (ID: {user['id']}, Role: {user['role']})")
            
            # Verify password
            if User.verify_password(user['password'], password):
                print("✓ Password verification SUCCESSFUL")
                
                # For doctor users, verify they have a doctor profile
                if user['role'] == 'doctor':
                    doctor = Doctor.get_by_user_id(user['id'])
                    if not doctor:
                        print(f"❌ Doctor profile missing for user {user['id']}")
                        flash('Your doctor profile is incomplete. Please contact support.', 'danger')
                        return redirect(url_for('auth.login'))
                    print(f"✓ Doctor profile found: {doctor['specialization']}")
                
                # For patient users, verify they have a patient profile
                elif user['role'] == 'patient':
                    patient = Patient.get_by_user_id(user['id'])
                    if not patient:
                        print(f"❌ Patient profile missing for user {user['id']}")
                        flash('Your patient profile is incomplete. Please contact support.', 'danger')
                        return redirect(url_for('auth.login'))
                    print(f"✓ Patient profile found")
                
                # Set session
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['role'] = user['role']
                
                flash(f'Welcome back, {user["name"]}!', 'success')
                
                # Redirect based on role
                if user['role'] == 'patient':
                    return redirect(url_for('patient.dashboard'))
                else:
                    return redirect(url_for('doctor.dashboard'))
            else:
                print("✗ Password verification FAILED")
                flash('Invalid password', 'danger')
        else:
            print(f"✗ No user found with email: {email}")
            flash('Invalid email or password', 'danger')
        
        print("="*60)
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('auth.login'))