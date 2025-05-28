
from flask import render_template, request, session, redirect, url_for, jsonify, flash
from app import app, db
from models import TroubleshootingCase, TroubleshootingStep, CaseFeedback
from troubleshooting_data import TROUBLESHOOTING_STEPS
from ai_assistant import TroubleshootingAI
import json
import time
import uuid
from datetime import datetime

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_case', methods=['POST'])
def start_case():
    # Get form data
    account_number = request.form.get('account_number')
    customer_name = request.form.get('customer_name')
    customer_phone = request.form.get('customer_phone')
    customer_email = request.form.get('customer_email')
    ont_type = request.form.get('ont_type')
    router_type = request.form.get('router_type')
    issue_type = request.form.get('issue_type')
    
    # Generate case number
    case_number = f"TSR-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    # Create customer info dict
    customer_info = {
        'account_number': account_number,
        'customer_name': customer_name,
        'customer_phone': customer_phone,
        'customer_email': customer_email
    }
    
    # Create new case
    case = TroubleshootingCase(
        session_id=str(uuid.uuid4()),
        case_number=case_number,
        customer_info=json.dumps(customer_info),
        ont_type=ont_type,
        router_type=router_type,
        issue_type=issue_type,
        status='in_progress',
        start_time=time.time()
    )
    
    db.session.add(case)
    db.session.commit()
    
    # Set session data
    session['case_id'] = case.id
    session['current_step'] = 'START'
    session['step_history'] = []
    
    return redirect(url_for('troubleshoot'))

@app.route('/restart_case')
def restart_case():
    # Clear session data
    session.clear()
    return redirect(url_for('index'))

@app.route('/troubleshoot')
def troubleshoot():
    case_id = session.get('case_id')
    if not case_id:
        flash('No active case found. Please start a new case.', 'warning')
        return redirect(url_for('index'))
    
    case = TroubleshootingCase.query.get_or_404(case_id)
    current_step_id = session.get('current_step', 'START')
    current_step = TROUBLESHOOTING_STEPS.get(current_step_id, TROUBLESHOOTING_STEPS['START'])
    
    # Calculate progress
    total_steps = len([k for k in TROUBLESHOOTING_STEPS.keys() if not k.endswith('_SUMMARY')])
    step_index = list(TROUBLESHOOTING_STEPS.keys()).index(current_step_id) + 1
    progress_percentage = (step_index / total_steps) * 100
    
    return render_template('troubleshoot_final.html',
                         case=case,
                         current_step_id=current_step_id,
                         current_step=current_step,
                         progress_percentage=progress_percentage,
                         step_index=step_index,
                         total_steps=total_steps)

@app.route('/next_step', methods=['POST'])
def next_step():
    case_id = session.get('case_id')
    if not case_id:
        return redirect(url_for('index'))
    
    current_step_id = session.get('current_step', 'START')
    current_step = TROUBLESHOOTING_STEPS.get(current_step_id)
    
    if not current_step:
        return redirect(url_for('troubleshoot'))
    
    # Store step data in session
    step_data = {}
    for field in current_step.get('input_fields', []):
        field_name = field['name']
        field_value = request.form.get(field_name)
        if field_value:
            step_data[field_name] = field_value
    
    # Store specific step data for AI analysis
    if current_step_id == 'SS_START':
        session['speed_test_data'] = step_data
    elif current_step_id == 'ALARM_STREAM_ANALYSIS':
        session['alarm_data'] = step_data
    
    # Handle AI recommendations step
    if current_step_id == 'ALARM_STREAM_ANALYSIS':
        # Generate AI recommendations
        ai_assistant = TroubleshootingAI()
        try:
            speed_test_data = session.get('speed_test_data', {})
            alarm_data = session.get('alarm_data', {})
            customer_info = TroubleshootingCase.query.get(case_id).get_customer_info()
            
            recommendations = ai_assistant.analyze_speed_test_and_alarms(
                speed_test_data, alarm_data, customer_info
            )
            session['ai_recommendations'] = recommendations
            session['ai_model_used'] = 'ChatGPT 4o-mini'
        except Exception as e:
            session['ai_recommendations'] = f"AI analysis temporarily unavailable. Please proceed with manual troubleshooting. Error: {str(e)}"
    
    # Determine next step
    next_step_id = None
    if 'next_step' in request.form:
        next_step_id = request.form['next_step']
    else:
        # Use the first option as default
        options = current_step.get('options', {})
        if options:
            next_step_id = list(options.values())[0]
    
    if next_step_id:
        session['current_step'] = next_step_id
        session.setdefault('step_history', []).append(current_step_id)
    
    return redirect(url_for('troubleshoot'))

@app.route('/start_troubleshooting', methods=['POST'])
def start_troubleshooting():
    try:
        # Get form data
        case_number = request.form.get('case_number')
        customer_name = request.form.get('customer_name')
        customer_phone = request.form.get('customer_phone')
        
        # Store in session
        session['case_number'] = case_number
        session['customer_name'] = customer_name
        session['customer_phone'] = customer_phone
        session['current_step_id'] = 'ROUTER_SELECTION'
        session['troubleshooting_data'] = {}
        session['session_start_time'] = time.time()
        
        return redirect(url_for('troubleshoot_wizard'))
    except Exception as e:
        flash(f'Error starting troubleshooting session: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/troubleshoot_wizard')
def troubleshoot_wizard():
    if 'case_number' not in session:
        flash('No active troubleshooting session found. Please start a new session.', 'warning')
        return redirect(url_for('index'))
    
    current_step_id = session.get('current_step_id', 'ROUTER_SELECTION')
    current_step = TROUBLESHOOTING_STEPS.get(current_step_id)
    
    if not current_step:
        flash('Invalid step in troubleshooting flow.', 'error')
        return redirect(url_for('index'))
    
    return render_template('troubleshoot_wizard.html', 
                         current_step=current_step,
                         current_step_id=current_step_id,
                         session_data=session)

@app.route('/submit_step', methods=['POST'])
def submit_step():
    if 'case_number' not in session:
        return jsonify({'error': 'No active session found'}), 400
    
    try:
        current_step_id = session.get('current_step_id')
        current_step = TROUBLESHOOTING_STEPS.get(current_step_id)
        
        if not current_step:
            return jsonify({'error': 'Invalid step'}), 400
        
        # Get form data
        form_data = {}
        
        # Handle input fields
        if 'input_fields' in current_step:
            for field in current_step['input_fields']:
                field_name = field['name']
                field_value = request.form.get(field_name)
                if field_value:
                    form_data[field_name] = field_value
        
        # Handle selected option
        selected_option = request.form.get('selected_option')
        if selected_option:
            form_data['selected_option'] = selected_option
        
        # Store step data
        if 'troubleshooting_data' not in session:
            session['troubleshooting_data'] = {}
        
        session['troubleshooting_data'][current_step_id] = form_data
        
        # Store Step 4 and Step 5 data for recommendations
        if current_step_id == 'WIFI_CHECK':
            session['step_4_data'] = form_data
        elif current_step_id == 'SPEED_TEST_CHECK':
            session['step_5_data'] = form_data
        
        # Determine next step
        next_step_id = None
        if selected_option and selected_option in current_step.get('options', {}):
            next_step_id = current_step['options'][selected_option]
        
        # Handle special cases
        if current_step_id == 'EXECUTE_TROUBLESHOOTING':
            issue_status = form_data.get('issue_status')
            if issue_status == 'resolved':
                next_step_id = 'ISSUE_RESOLVED'
            elif issue_status == 'improved':
                next_step_id = 'ISSUE_IMPROVED'
            elif issue_status == 'no_change':
                next_step_id = 'ISSUE_NO_CHANGE'
        
        if next_step_id:
            session['current_step_id'] = next_step_id
            return jsonify({'success': True, 'next_step': next_step_id})
        else:
            return jsonify({'error': 'No next step defined'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_recommendations')
def get_recommendations():
    try:
        # Get stored data from Steps 4 and 5
        step_4_data = session.get('step_4_data', {})
        step_5_data = session.get('step_5_data', {})
        troubleshooting_data = session.get('troubleshooting_data', {})
        
        # Build selections object for recommendations engine
        selections = {}
        
        # From Step 4 (Wi-Fi Check)
        if step_4_data:
            selections['connectionType'] = step_4_data.get('connection_type', 'wifi')
            selections['band'] = step_4_data.get('wifi_band', '5')
            selections['rssi'] = 'low' if step_4_data.get('signal_strength') == 'poor' else 'good'
            selections['deviceBandCap'] = step_4_data.get('device_capability', 'dual')
        
        # From Step 5 (Speed Test)
        if step_5_data:
            speed = int(step_5_data.get('speed_before', 0))
            if speed < 50:
                selections['speedBucket'] = 'sub50'
            elif speed < 100:
                selections['speedBucket'] = 'sub100'
            elif speed < 300:
                selections['speedBucket'] = 'sub300'
            else:
                selections['speedBucket'] = 'good'
        
        # From other steps
        router_data = troubleshooting_data.get('ROUTER_SELECTION', {})
        if router_data.get('router_type') == 'Eero':
            selections['routerType'] = 'eero'
        
        return jsonify({
            'success': True,
            'selections': selections
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/troubleshoot_final')
def troubleshoot_final():
    if 'case_number' not in session:
        flash('No active troubleshooting session found.', 'warning')
        return redirect(url_for('index'))
    
    current_step_id = session.get('current_step_id', 'EXECUTE_TROUBLESHOOTING')
    current_step = TROUBLESHOOTING_STEPS.get(current_step_id)
    
    return render_template('troubleshoot_final.html',
                         current_step=current_step,
                         current_step_id=current_step_id,
                         session_data=session)

@app.route('/generate_report')
def generate_report():
    if 'case_number' not in session:
        return jsonify({'error': 'No active session found'}), 400
    
    try:
        # Generate comprehensive report
        troubleshooting_data = session.get('troubleshooting_data', {})
        
        report = {
            'case_number': session.get('case_number'),
            'customer_name': session.get('customer_name'),
            'customer_phone': session.get('customer_phone'),
            'session_start': session.get('session_start_time'),
            'steps_completed': troubleshooting_data,
            'escalation_reason': 'Issue persists after multiple troubleshooting attempts'
        }
        
        return jsonify({
            'success': True,
            'report': report
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/recover_session')
def recover_session():
    # Simple session recovery - redirect to start
    return redirect(url_for('index'))
