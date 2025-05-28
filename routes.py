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
    case = TroubleshootingCase()
    case.session_id = str(uuid.uuid4())
    case.case_number = case_number
    case.customer_info = json.dumps(customer_info)
    case.ont_type = ont_type
    case.router_type = router_type
    case.issue_type = issue_type
    case.status = 'in_progress'
    case.start_time = time.time()
    
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
            case = TroubleshootingCase.query.get(case_id)
            customer_info = json.loads(case.customer_info) if case.customer_info else {}
            
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

@app.route('/case_summary/<int:case_id>')
def case_summary(case_id):
    case = TroubleshootingCase.query.get_or_404(case_id)
    return render_template('case_summary.html', case=case)

@app.route('/generate_report/<int:case_id>')
def generate_report(case_id):
    case = TroubleshootingCase.query.get_or_404(case_id)
    return render_template('dispatch_report.html', case=case)