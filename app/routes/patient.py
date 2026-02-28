# app/routes/patient.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.models import Patient, Appointment, Doctor
from app.utils import login_required, role_required, get_available_time_slots, validate_appointment_date
from datetime import datetime
import traceback

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/dashboard')
@login_required
@role_required('patient')
def dashboard():
    try:
        # Get patient details
        patient = Patient.get_by_user_id(session['user_id'])
        
        if not patient:
            flash('Patient profile not found', 'danger')
            return redirect(url_for('auth.logout'))
        
        # Get all available doctors
        doctors = Patient.get_all_doctors()
        
        # Get patient's appointments
        appointments = Appointment.get_patient_appointments(patient['id'])
        
        # Get upcoming appointments (approved and future dates)
        upcoming_appointments = []
        today = datetime.now().date()
        for apt in appointments:
            if apt['status'] == 'Approved' and apt['appointment_date'] >= str(today):
                upcoming_appointments.append(apt)
        
        return render_template('patient_dashboard.html', 
                             patient=patient, 
                             doctors=doctors, 
                             appointments=appointments,
                             upcoming_appointments=upcoming_appointments[:3],
                             time_slots=get_available_time_slots(),
                             now=datetime.now())
    except Exception as e:
        print(f"Error in dashboard: {e}")
        traceback.print_exc()
        flash('Error loading dashboard', 'danger')
        return redirect(url_for('auth.logout'))

@patient_bp.route('/check-slot-availability', methods=['POST'])
@login_required
@role_required('patient')
def check_slot_availability():
    try:
        doctor_id = request.form.get('doctor_id')
        appointment_date = request.form.get('appointment_date')
        time_slot = request.form.get('time_slot')
        
        print(f"\n--- Checking slot availability ---")
        print(f"Doctor ID: {doctor_id}")
        print(f"Date: {appointment_date}")
        print(f"Time: {time_slot}")
        
        if not all([doctor_id, appointment_date, time_slot]):
            return jsonify({'available': False, 'message': 'Missing required fields'})
        
        # Get patient ID
        patient = Patient.get_by_user_id(session['user_id'])
        if not patient:
            return jsonify({'available': False, 'message': 'Patient not found'})
        
        # Check if slot is available
        slot_available = Appointment.check_slot_available(doctor_id, appointment_date, time_slot)
        print(f"Slot available: {slot_available}")
        
        if not slot_available:
            return jsonify({'available': False, 'message': 'This time slot is already booked'})
        
        # Check if patient already booked this slot
        patient_duplicate = Appointment.check_patient_duplicate(
            patient['id'], doctor_id, appointment_date, time_slot
        )
        print(f"Patient duplicate: {patient_duplicate}")
        
        if patient_duplicate:
            return jsonify({'available': False, 'message': 'You have already booked this time slot'})
        
        return jsonify({'available': True, 'message': 'Slot is available for booking'})
        
    except Exception as e:
        print(f"Error checking availability: {e}")
        traceback.print_exc()
        return jsonify({'available': False, 'message': f'Error: {str(e)}'})

@patient_bp.route('/book-appointment', methods=['POST'])
@login_required
@role_required('patient')
def book_appointment():
    try:
        # Get form data
        doctor_id = request.form.get('doctor_id')
        appointment_date = request.form.get('appointment_date')
        time_slot = request.form.get('time_slot')
        symptoms = request.form.get('symptoms', '').strip()
        
        print("\n" + "="*50)
        print("BOOK APPOINTMENT ATTEMPT")
        print("="*50)
        print(f"Doctor ID: {doctor_id}")
        print(f"Date: {appointment_date}")
        print(f"Time: {time_slot}")
        print(f"Symptoms: {symptoms}")
        
        # Validate required fields
        if not all([doctor_id, appointment_date, time_slot, symptoms]):
            missing = []
            if not doctor_id: missing.append('doctor')
            if not appointment_date: missing.append('date')
            if not time_slot: missing.append('time')
            if not symptoms: missing.append('symptoms')
            return jsonify({'success': False, 'message': f'Missing fields: {", ".join(missing)}'})
        
        # Get patient ID
        patient = Patient.get_by_user_id(session['user_id'])
        if not patient:
            return jsonify({'success': False, 'message': 'Patient profile not found'})
        
        print(f"Patient ID: {patient['id']}")
        
        # Validate date (not in past)
        if not validate_appointment_date(appointment_date):
            return jsonify({'success': False, 'message': 'Cannot book appointment for past dates'})
        
        # Check if slot is available
        if not Appointment.check_slot_available(doctor_id, appointment_date, time_slot):
            return jsonify({'success': False, 'message': 'This time slot is already booked'})
        
        # Check if patient already booked this slot
        if Appointment.check_patient_duplicate(patient['id'], doctor_id, appointment_date, time_slot):
            return jsonify({'success': False, 'message': 'You have already booked this time slot'})
        
        # Create appointment
        success, result = Appointment.create(
            patient['id'], doctor_id, appointment_date, time_slot, symptoms
        )
        
        if success:
            print(f"✓ Appointment created successfully with ID: {result}")
            return jsonify({'success': True, 'message': 'Appointment booked successfully!'})
        else:
            print(f"✗ Failed to create appointment: {result}")
            return jsonify({'success': False, 'message': f'Failed to book: {result}'})
            
    except Exception as e:
        print(f"!!! Error in book_appointment: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})