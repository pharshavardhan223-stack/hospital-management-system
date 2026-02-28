from functools import wraps
from flask import session, redirect, url_for, flash
from datetime import datetime, timedelta

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] != required_role:
                flash('Access denied. Insufficient permissions.', 'danger')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_available_time_slots():
    """Return list of available time slots for appointments"""
    return [
        '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM',
        '02:00 PM', '02:30 PM', '03:00 PM', '03:30 PM', '04:00 PM', '04:30 PM'
    ]

def validate_appointment_date(appointment_date):
    """Check if appointment date is not in the past"""
    try:
        appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        today = datetime.now().date()
        return appointment_date >= today
    except:
        return False

def get_status_badge_class(status):
    """Return Bootstrap badge class based on status"""
    badges = {
        'Pending': 'warning',
        'Approved': 'success',
        'Rejected': 'danger'
    }
    return badges.get(status, 'secondary')