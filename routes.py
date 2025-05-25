from flask import render_template, request, session, redirect, url_for, flash, jsonify
from datetime import datetime
import uuid
import json
from app import app, db
from models import TroubleshootingCase, TroubleshootingStep
from troubleshooting_data import TROUBLESHOOTING_STEPS, EQUIPMENT_INFO

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_case', methods=['POST'])
def start_case():
    # Generate unique case number
    case_number = f"TSR-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    # Get customer information
    customer_info = {
        'name': request.form.get('customer_name', ''),
        'account': request.form.get('account_number', ''),
        'phone': request.form.get('phone_number', ''),
        'email': request.form.get('email', '')
    }
    
    # Create new case
    case = TroubleshootingCase(
        session_id=session.get('session_id', str(uuid.uuid4())),
        case_number=case_number,
        start_time=datetime.now().timestamp()
    )
    case.set_customer_info(customer_info)
    
    db.session.add(case)
    db.session.commit()
    
    # Store case ID in session
    session['case_id'] = case.id
    session['current_step'] = 'START'
    session['step_history'] = []
    
    return redirect(url_for('troubleshoot'))

@app.route('/troubleshoot')
def troubleshoot():
    case_id = session.get('case_id')
    if not case_id:
        flash('No active troubleshooting case found. Please start a new case.', 'warning')
        return redirect(url_for('index'))
    
    case = TroubleshootingCase.query.get_or_404(case_id)
    current_step_id = session.get('current_step', 'START')
    step_history = session.get('step_history', [])
    
    current_step = TROUBLESHOOTING_STEPS.get(current_step_id, {})
    
    # Calculate progress
    total_possible_steps = len(TROUBLESHOOTING_STEPS)
    current_progress = min(len(step_history) + 1, total_possible_steps)
    progress_percentage = (current_progress / total_possible_steps) * 100
    
    return render_template('troubleshoot_simple.html', 
                         case=case,
                         current_step=current_step,
                         current_step_id=current_step_id,
                         step_history=step_history,
                         progress_percentage=progress_percentage,
                         step_number=len(step_history) + 1)

@app.route('/next_step', methods=['POST'])
def next_step():
    case_id = session.get('case_id')
    if not case_id:
        return redirect(url_for('index'))
    
    case = TroubleshootingCase.query.get_or_404(case_id)
    current_step_id = session.get('current_step')
    next_step_id = request.form.get('next_step')
    action_taken = request.form.get('action_taken', '')
    notes = request.form.get('notes', '')
    
    # Collect input field data
    input_data = {}
    current_step_data = TROUBLESHOOTING_STEPS.get(current_step_id, {})
    if current_step_data.get('input_fields'):
        for field in current_step_data['input_fields']:
            field_value = request.form.get(field['name'], '')
            if field_value:
                input_data[field['name']] = field_value
    
    # Format input data for notes if present
    input_notes = ""
    if input_data:
        input_notes = "\n".join([f"{key}: {value}" for key, value in input_data.items()])
        if notes:
            notes = f"{input_notes}\n\nAdditional Notes: {notes}"
        else:
            notes = input_notes

    # Log the step
    step = TroubleshootingStep(
        case_id=case.id,
        step_id=current_step_id,
        step_name=TROUBLESHOOTING_STEPS.get(current_step_id, {}).get('question', ''),
        action_taken=action_taken,
        notes=notes
    )
    db.session.add(step)
    
    # Update case information based on step
    if current_step_id == 'START':
        case.ont_type = action_taken
    elif current_step_id == 'ROUTER_CHECK':
        case.router_type = action_taken
    elif current_step_id == 'ISSUE_TYPE':
        case.issue_type = action_taken
    
    # Update session
    step_history = session.get('step_history', [])
    step_history.append({
        'step_id': current_step_id,
        'action': action_taken,
        'timestamp': datetime.now().isoformat()
    })
    session['step_history'] = step_history
    session['current_step'] = next_step_id
    
    # Check if this is an end step
    next_step = TROUBLESHOOTING_STEPS.get(next_step_id, {})
    if next_step.get('instruction') and not next_step.get('options'):
        # This is an end step
        case.resolution = next_step['instruction']
        case.status = 'resolved'
        case.end_time = datetime.now().timestamp()
        case.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Troubleshooting case completed successfully!', 'success')
        return redirect(url_for('case_summary', case_id=case.id))
    
    db.session.commit()
    return redirect(url_for('troubleshoot'))

@app.route('/add_note', methods=['POST'])
def add_note():
    case_id = session.get('case_id')
    if not case_id:
        return jsonify({'success': False, 'message': 'No active case'})
    
    note_text = request.form.get('note')
    if note_text:
        step = TroubleshootingStep(
            case_id=case_id,
            step_id='NOTE',
            step_name='Additional Note',
            notes=note_text
        )
        db.session.add(step)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Note added successfully'})
    
    return jsonify({'success': False, 'message': 'Note cannot be empty'})

@app.route('/case_summary/<int:case_id>')
def case_summary(case_id):
    case = TroubleshootingCase.query.get_or_404(case_id)
    
    # Check if this is a hard-down case that needs dispatch report
    dispatch_report = None
    if case.status == 'resolved' and any(step.step_id.startswith('HARD_DOWN') for step in case.steps):
        dispatch_report = generate_dispatch_report(case)
    
    return render_template('case_summary.html', case=case, dispatch_report=dispatch_report)

@app.route('/dispatch_report/<int:case_id>')
def dispatch_report(case_id):
    case = TroubleshootingCase.query.get_or_404(case_id)
    report = generate_dispatch_report(case)
    return render_template('dispatch_report.html', case=case, report=report)

def generate_dispatch_report(case):
    """Generate comprehensive dispatch report for field service"""
    customer_info = case.get_customer_info()
    
    # Collect all hard-down data from steps
    hard_down_data = {}
    for step in case.steps:
        if step.step_id.startswith('HARD_DOWN') and step.notes:
            lines = step.notes.split('\n')
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    hard_down_data[key.strip()] = value.strip()
    
    # Format router information
    router_info = []
    if hard_down_data.get('router_1_id'):
        router_info.append(f"Primary: {hard_down_data['router_1_id']}")
    if hard_down_data.get('router_2_id'):
        router_info.append(f"Secondary: {hard_down_data['router_2_id']}")
    if hard_down_data.get('router_3_id'):
        router_info.append(f"Third: {hard_down_data['router_3_id']}")
    
    # Format the dispatch report
    report = {
        'case_number': case.case_number,
        'customer_name': customer_info.get('name', 'N/A'),
        'phone_number': customer_info.get('phone', 'N/A'),
        'email': customer_info.get('email', 'N/A'),
        'account_number': customer_info.get('account', 'N/A'),
        'verified_head_end_hub': hard_down_data.get('hub_name', 'N/A'),
        'ont_id': hard_down_data.get('ont_id', 'N/A'),
        'router_information': ' | '.join(router_info) if router_info else 'N/A',
        'issue_customer_reporting': 'No Internet',
        'alarm_code': 'ONT Loss of PHY Layer',
        'timeframe_issue_happened': hard_down_data.get('alarm_start_time', 'N/A'),
        'alarm_details': hard_down_data.get('alarm_details', 'N/A'),
        'speed_test_results': 'N/A (Hard Down)',
        'devices_disconnecting': 'N/A',
        'network_stable': 'N/A',
        'light_levels_olt': hard_down_data.get('olt_light_level', 'N/A'),
        'light_levels_ont': hard_down_data.get('ont_light_level', 'N/A'),
        'l2_user_aligned': 'YES',
        'wifi_interference': 'N/A',
        'equipment_rebooted': 'YES',
        'connections_verified': 'YES',
        'troubleshooting_steps': 'Rebooted ONT and router, reseated fiber/ethernet connections',
        'total_onts_on_pon': hard_down_data.get('total_onts', 'N/A'),
        'alarmed_onts': hard_down_data.get('alarmed_onts', 'N/A'),
        'other_customers_affected': 'YES' if int(hard_down_data.get('alarmed_onts', '0')) > 1 else 'NO',
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'case_duration': case.get_duration()
    }
    
    return report

# Search functionality removed - not needed for troubleshooting workflow

@app.route('/go_back')
def go_back():
    step_history = session.get('step_history', [])
    if len(step_history) > 1:
        # Remove the current step and go back to previous
        step_history.pop()
        session['step_history'] = step_history
        previous_step = step_history[-1] if step_history else {'step_id': 'START'}
        session['current_step'] = previous_step['step_id']
    else:
        session['current_step'] = 'START'
        session['step_history'] = []
    
    return redirect(url_for('troubleshoot'))

@app.route('/restart_case')
def restart_case():
    # Clear session data
    session.pop('case_id', None)
    session.pop('current_step', None)
    session.pop('step_history', None)
    
    flash('Case restarted. You can begin a new troubleshooting session.', 'info')
    return redirect(url_for('index'))
