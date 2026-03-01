# app/routes/chat.py
from flask import Blueprint, render_template, jsonify, session, redirect, url_for, request
from app.models import Doctor, Patient, Conversation, Message
from app.utils import login_required, role_required
from app import get_db
from datetime import datetime
import json
import traceback

chat_bp = Blueprint('chat', __name__)

# ===== CONVERSATION ROUTES =====

@chat_bp.route('/inbox')
@login_required
def inbox():
    """Main inbox page showing all conversations"""
    try:
        if session['role'] == 'doctor':
            doctor = Doctor.get_by_user_id(session['user_id'])
            if not doctor:
                return "Doctor not found", 404
            conversations = Conversation.get_for_doctor(doctor['id'])
            return render_template('chat_inbox.html', 
                                 conversations=conversations, 
                                 role='doctor',
                                 user_name=session['user_name'])
        else:
            patient = Patient.get_by_user_id(session['user_id'])
            if not patient:
                return "Patient not found", 404
            conversations = Conversation.get_for_patient(patient['id'])
            return render_template('chat_inbox.html', 
                                 conversations=conversations, 
                                 role='patient',
                                 user_name=session['user_name'])
    except Exception as e:
        print(f"Error in inbox: {e}")
        traceback.print_exc()
        return str(e), 500

@chat_bp.route('/conversation/<int:conversation_id>')
@login_required
def conversation(conversation_id):
    """View a specific conversation"""
    try:
        # Get messages
        messages = Message.get_for_conversation(conversation_id)
        
        # Mark messages as read
        Message.mark_conversation_read(conversation_id, session['role'])
        Conversation.mark_read(conversation_id, session['role'])
        
        # Get other party info
        db = get_db()
        cursor = db.cursor()
        
        if session['role'] == 'doctor':
            cursor.execute('''
                SELECT u.name, p.age, p.gender, p.id 
                FROM conversations c
                JOIN patients p ON c.patient_id = p.id
                JOIN users u ON p.user_id = u.id
                WHERE c.id = ?
            ''', (conversation_id,))
            other = cursor.fetchone()
            if other:
                other_name = other[0]
                other_info = f"Age: {other[1]} | {other[2]}"
                other_id = other[3]
            else:
                other_name = "Unknown"
                other_info = ""
                other_id = None
        else:
            cursor.execute('''
                SELECT u.name, d.specialization, d.id 
                FROM conversations c
                JOIN doctors d ON c.doctor_id = d.id
                JOIN users u ON d.user_id = u.id
                WHERE c.id = ?
            ''', (conversation_id,))
            other = cursor.fetchone()
            if other:
                other_name = "Dr. " + other[0]
                other_info = other[1]
                other_id = other[2]
            else:
                other_name = "Unknown"
                other_info = ""
                other_id = None
        
        db.close()
        
        return render_template('chat_conversation.html',
                             messages=messages,
                             conversation_id=conversation_id,
                             role=session['role'],
                             other_name=other_name,
                             other_info=other_info,
                             other_id=other_id,
                             user_name=session['user_name'])
    except Exception as e:
        print(f"Error in conversation: {e}")
        traceback.print_exc()
        return str(e), 500

@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """Send a new message"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'})
        
        conversation_id = data.get('conversation_id')
        message_text = data.get('message', '').strip()
        is_emergency = data.get('is_emergency', False)
        
        print(f"Received message request: conv={conversation_id}, msg={message_text}, emergency={is_emergency}")
        
        if not message_text:
            return jsonify({'success': False, 'error': 'Message cannot be empty'})
        
        if not conversation_id:
            return jsonify({'success': False, 'error': 'Conversation ID is required'})
        
        # Get sender ID
        if session['role'] == 'doctor':
            doctor = Doctor.get_by_user_id(session['user_id'])
            if not doctor:
                return jsonify({'success': False, 'error': 'Doctor not found'})
            sender_id = doctor['id']
            print(f"Doctor sender ID: {sender_id}")
        else:
            patient = Patient.get_by_user_id(session['user_id'])
            if not patient:
                return jsonify({'success': False, 'error': 'Patient not found'})
            sender_id = patient['id']
            print(f"Patient sender ID: {sender_id}")
        
        # Send message
        result = Message.send(
            conversation_id=conversation_id,
            sender_id=sender_id,
            sender_role=session['role'],
            message=message_text,
            is_emergency=is_emergency
        )
        
        print(f"Message sent successfully: {result}")
        
        return jsonify({
            'success': True,
            'message_id': result['id'],
            'time': result['time']
        })
    except Exception as e:
        print(f"Error sending message: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@chat_bp.route('/start/<int:doctor_id>')
@login_required
@role_required('patient')
def start_conversation(doctor_id):
    """Start a new conversation with a doctor"""
    try:
        patient = Patient.get_by_user_id(session['user_id'])
        if not patient:
            return "Patient not found", 404
        
        # Check if conversation exists
        conv_id = Conversation.get_or_create(doctor_id, patient['id'])
        
        return redirect(url_for('chat.conversation', conversation_id=conv_id))
    except Exception as e:
        print(f"Error starting conversation: {e}")
        traceback.print_exc()
        return str(e), 500

@chat_bp.route('/select-doctor')
@login_required
@role_required('patient')
def select_doctor():
    """Show all doctors for patient to start a chat"""
    try:
        doctors = Patient.get_all_doctors()
        return render_template('select_doctor.html', doctors=doctors)
    except Exception as e:
        print(f"Error in select_doctor: {e}")
        traceback.print_exc()
        return str(e), 500

@chat_bp.route('/unread-count')
@login_required
def unread_count():
    """Get unread message count for current user"""
    try:
        if session['role'] == 'doctor':
            doctor = Doctor.get_by_user_id(session['user_id'])
            if not doctor:
                return jsonify({'count': 0})
            count = Message.get_unread_count(doctor['id'], 'doctor')
        else:
            patient = Patient.get_by_user_id(session['user_id'])
            if not patient:
                return jsonify({'count': 0})
            count = Message.get_unread_count(patient['id'], 'patient')
        
        return jsonify({'count': count})
    except Exception as e:
        print(f"Error getting unread count: {e}")
        traceback.print_exc()
        return jsonify({'count': 0})

@chat_bp.route('/api/messages/<int:conversation_id>')
@login_required
def get_messages_api(conversation_id):
    """API endpoint to get new messages"""
    try:
        after = request.args.get('after', 0, type=int)
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT * FROM messages 
            WHERE conversation_id = ? AND id > ?
            ORDER BY created_at ASC
        ''', (conversation_id, after))
        
        messages = cursor.fetchall()
        db.close()
        
        messages_list = []
        for msg in messages:
            time_str = msg[8]  # created_at
            if time_str and ' ' in time_str:
                time_formatted = time_str.split(' ')[1][:5]
            else:
                time_formatted = '00:00'
                
            messages_list.append({
                'id': msg[0],
                'message': msg[4],
                'sender_role': msg[3],
                'is_emergency': msg[7],
                'time': time_formatted
            })
        
        return jsonify({'messages': messages_list})
    except Exception as e:
        print(f"Error getting messages: {e}")
        traceback.print_exc()
        return jsonify({'messages': []})