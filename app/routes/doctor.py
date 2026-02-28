from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import Doctor, Appointment
from app.utils import login_required, role_required
from datetime import datetime

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/dashboard')
@login_required
@role_required('doctor')
def dashboard():
    # Get doctor details
    doctor = Doctor.get_by_user_id(session['user_id'])
    
    if not doctor:
        flash('Doctor profile not found', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get pending appointments
    pending_appointments = Doctor.get_pending_appointments(doctor['id'])
    
    # Get today's appointments
    todays_appointments = Doctor.get_todays_appointments(doctor['id'])
    
    return render_template('doctor_dashboard.html',
                         doctor=doctor,
                         pending_appointments=pending_appointments,
                         todays_appointments=todays_appointments,
                         now=datetime.now())

@doctor_bp.route('/appointment/<int:appointment_id>/approve')
@login_required
@role_required('doctor')
def approve_appointment(appointment_id):
    # Update appointment status
    Appointment.update_status(appointment_id, 'Approved')
    flash('Appointment approved successfully', 'success')
    return redirect(url_for('doctor.dashboard'))

@doctor_bp.route('/appointment/<int:appointment_id>/reject', methods=['POST'])
@login_required
@role_required('doctor')
def reject_appointment(appointment_id):
    rejection_reason = request.form.get('rejection_reason')
    
    if not rejection_reason or not rejection_reason.strip():
        flash('Please provide a reason for rejection', 'danger')
        return redirect(url_for('doctor.dashboard'))
    
    # Update appointment status with rejection reason
    Appointment.update_status(appointment_id, 'Rejected', rejection_reason.strip())
    flash('Appointment rejected successfully', 'success')
    return redirect(url_for('doctor.dashboard'))

@doctor_bp.route('/appointments-by-date', methods=['POST'])
@login_required
@role_required('doctor')
def appointments_by_date():
    doctor = Doctor.get_by_user_id(session['user_id'])
    selected_date = request.form.get('appointment_date')
    
    appointments_by_date = Doctor.get_appointments_by_date(doctor['id'], selected_date)
    pending_appointments = Doctor.get_pending_appointments(doctor['id'])
    todays_appointments = Doctor.get_todays_appointments(doctor['id'])
    
    return render_template('doctor_dashboard.html',
                         doctor=doctor,
                         pending_appointments=pending_appointments,
                         todays_appointments=todays_appointments,
                         appointments_by_date=appointments_by_date,
                         selected_date=selected_date,
                         now=datetime.now())