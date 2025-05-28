from flask import render_template, request, session, redirect, url_for, flash, jsonify
from datetime import datetime
import uuid
import json
from app import app, db
from models import TroubleshootingCase, TroubleshootingStep, CaseFeedback
from ai_assistant import TroubleshootingAI
from troubleshooting_data import TROUBLESHOOTING_STEPS, EQUIPMENT_INFO

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_case', methods=['POST'])
def start_case():
    # Generate unique case number
    case_number = f"TSR-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    # Get customer information - only account number for security compliance
    customer_info = {
        'account': request.form.get('account_number', ''),
        'name': '',  # Will be collected during troubleshooting if needed
        'phone': '',  # Will be collected during troubleshooting if needed
        'email': '',  # Will be collected during troubleshooting if needed
        'address': ''  # Will be collected during troubleshooting if needed
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
    
    # Store case ID in session and make it permanent
    session.permanent = True
    session['case_id'] = case.id
    session['current_step'] = 'START'
    session['step_history'] = []
    
    return redirect(url_for('troubleshoot_wizard_step', step=1, case_id=case.id))

@app.route('/troubleshoot_wizard')
def troubleshoot_wizard():
    # Get case_id from URL or find most recent active case
    case_id = request.args.get('case_id')
    
    if not case_id:
        # Find most recent active case
        recent_case = TroubleshootingCase.query.filter_by(status='in_progress').order_by(TroubleshootingCase.created_at.desc()).first()
        if recent_case:
            # Redirect with case_id in URL
            return redirect(url_for('troubleshoot_wizard', case_id=recent_case.id))
        else:
            return redirect(url_for('index'))
    
    # Store in session but don't depend on it
    session['case_id'] = case_id
    
    case = TroubleshootingCase.query.get_or_404(case_id)
    
    # Start with equipment selection wizard - Step 1
    return redirect(url_for('troubleshoot_wizard_step', step=1, case_id=case.id))

@app.route('/troubleshoot_wizard/<int:step>')
def troubleshoot_wizard_step(step):
    case_id = request.args.get('case_id') or session.get('case_id')
    
    if not case_id:
        recent_case = TroubleshootingCase.query.filter_by(status='in_progress').order_by(TroubleshootingCase.created_at.desc()).first()
        if recent_case:
            return redirect(url_for('troubleshoot_wizard_step', step=step, case_id=recent_case.id))
        else:
            return redirect(url_for('index'))
    
    session['case_id'] = case_id
    
    case = TroubleshootingCase.query.get_or_404(case_id)
    
    step_titles = {
        1: "Equipment Identification",
        2: "Router Selection", 
        3: "Run Diagnostics",
        4: "Log & Report"
    }
    
    return render_template('troubleshoot_wizard.html', 
                         case=case,
                         current_step=step,
                         step_titles=step_titles)

@app.route('/troubleshoot')
def troubleshoot():
    # ALWAYS find the most recent case - no session dependency
    recent_case = TroubleshootingCase.query.filter_by(status='in_progress').order_by(TroubleshootingCase.created_at.desc()).first()
    
    if not recent_case:
        return redirect(url_for('index'))
    
    # Force the case_id into session
    session['case_id'] = recent_case.id
    case_id = recent_case.id
    
    case = TroubleshootingCase.query.get_or_404(case_id)
    current_step_id = session.get('current_step', 'START')
    step_history = session.get('step_history', [])
    
    current_step = TROUBLESHOOTING_STEPS.get(current_step_id, {})
    
    # Calculate progress
    total_possible_steps = len(TROUBLESHOOTING_STEPS)
    current_progress = min(len(step_history) + 1, total_possible_steps)
    progress_percentage = (current_progress / total_possible_steps) * 100
    
    return render_template('troubleshoot_final.html', 
                         case=case,
                         current_step=current_step,
                         current_step_id=current_step_id,
                         step_history=step_history,
                         progress_percentage=progress_percentage,
                         step_number=len(step_history) + 1)

@app.route('/next_step', methods=['POST'])
def next_step():
    # Get case_id from form or session, or find most recent case
    case_id = request.form.get('case_id') or session.get('case_id')
    
    if not case_id:
        recent_case = TroubleshootingCase.query.filter_by(status='in_progress').order_by(TroubleshootingCase.created_at.desc()).first()
        if recent_case:
            case_id = recent_case.id
            session['case_id'] = case_id
        else:
            return redirect(url_for('index'))
    
    case = TroubleshootingCase.query.get_or_404(case_id)
    current_step = int(request.form.get('current_step', 1))
    
    # Handle wizard step progression
    if current_step == 1:
        # Step 1: ONT Selection (simplified)
        ont_type = request.form.get('ont_type')
        if ont_type:
            case.ont_type = ont_type
            case.ont_id = None  # No longer collecting ONT ID
            db.session.commit()
            return redirect(url_for('troubleshoot_wizard_step', step=2, case_id=case.id))
    
    elif current_step == 2:
        # Step 2: Router Selection (simplified)
        router_type = request.form.get('router_type')
        if router_type:
            case.router_type = router_type
            case.router_id = None  # No longer collecting Router ID
            db.session.commit()
            return redirect(url_for('troubleshoot_wizard_step', step=3, case_id=case.id))
    
    elif current_step == 3:
        # Step 3: Issue Classification
        issue_type = request.form.get('issue_type')
        issue_description = request.form.get('issue_description', '')
        if issue_type:
            case.issue_type = issue_type
            # Store issue description in customer info if provided
            if issue_description:
                customer_info = case.get_customer_info()
                customer_info['issue_description'] = issue_description
                case.set_customer_info(customer_info)
            db.session.commit()
            
            # Branch to specific troubleshooting path based on issue type
            if issue_type == 'Complete Outage':
                session['current_step'] = 'START'
            elif issue_type == 'Slow Speeds':
                session['current_step'] = 'SS_START'
            elif issue_type == 'Intermittent Issue':
                session['current_step'] = 'CHECK_WIFI_ENV'
            else:
                session['current_step'] = 'START'
            
            session['step_history'] = []
            session['issue_type'] = issue_type
            return redirect(url_for('troubleshoot'))
    
    # Fallback to original logic for troubleshooting steps
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
            # Check for required fields
            elif field.get('required', False):
                flash(f'Please fill in the required field: {field["label"]}', 'error')
                return redirect(url_for('troubleshoot'))
    
    # Store dispatch data for Teams summary
    if current_step_id == 'DISPATCH_CHECK' and input_data:
        session['dispatch_data'] = input_data
    
    # Handle AI recommendations step
    if next_step_id == 'AI_RECOMMENDATIONS':
        # Collect speed test and alarm data from session
        speed_test_data = {}
        alarm_data = {}
        
        # Get speed test data from current step or session
        if current_step_id == 'SPEED_TEST_DOCUMENTATION':
            speed_test_data = input_data
            session['speed_test_data'] = speed_test_data
        elif current_step_id == 'ALARM_STREAM_ANALYSIS':
            alarm_data = input_data
            session['alarm_data'] = alarm_data
            speed_test_data = session.get('speed_test_data', {})
        else:
            speed_test_data = session.get('speed_test_data', {})
            alarm_data = session.get('alarm_data', {})
        
        # Get customer info for AI analysis
        customer_info = case.get_customer_info()
        customer_info.update({
            'ont_type': case.ont_type,
            'router_type': case.router_type,
            'speed_package': customer_info.get('speed_package', 'N/A')
        })
        
        # Generate AI recommendations
        try:
            ai_assistant = TroubleshootingAI()
            ai_result = ai_assistant.analyze_speed_test_and_alarms(
                speed_test_data, alarm_data, customer_info
            )
            
            if ai_result['success']:
                session['ai_recommendations'] = ai_result['recommendations']
                session['ai_model_used'] = ai_result['model_used']
            else:
                session['ai_recommendations'] = ai_result.get('fallback_recommendations', 'Unable to generate recommendations at this time.')
                session['ai_error'] = ai_result.get('error', 'Unknown error')
                
        except Exception as e:
            session['ai_recommendations'] = f"Error generating AI recommendations: {str(e)}"
            session['ai_error'] = str(e)
    
    # Smart validation for slow speeds light levels
    if current_step_id == 'SS_START' and input_data:
        ont_rx_power = input_data.get('ont_rx_power', '')
        olt_tx_power = input_data.get('olt_tx_power', '')
        alarm_type_1 = input_data.get('alarm_type_1', '')
        alarm_status_1 = input_data.get('alarm_status_1', '')
        
        # Auto-validate light levels and route intelligently
        if ont_rx_power and olt_tx_power:
            try:
                rx_power = float(ont_rx_power)
                tx_power = float(olt_tx_power)
                
                # Check if levels are within spec (-10 to -25 dBm)
                rx_in_spec = -25 <= rx_power <= -10
                tx_in_spec = -25 <= tx_power <= -10
                
                # Check if gap is <= 5 dB
                power_gap = abs(rx_power - tx_power)
                gap_ok = power_gap <= 5
                
                # Determine criticality based on alarm type
                critical_alarms = ['Loss of PHY Layer', 'Dying Gasp', 'High Optical RX Power', 'Low Optical RX Power']
                alarm_critical = alarm_type_1 in critical_alarms
                
                # Store validation results in session for next step
                session['light_validation'] = {
                    'rx_power': rx_power,
                    'tx_power': tx_power,
                    'rx_in_spec': rx_in_spec,
                    'tx_in_spec': tx_in_spec,
                    'power_gap': power_gap,
                    'gap_ok': gap_ok,
                    'overall_ok': rx_in_spec and tx_in_spec and gap_ok,
                    'alarm_type': alarm_type_1,
                    'alarm_status': alarm_status_1,
                    'alarm_critical': alarm_critical
                }
                
                # Auto-route based on validation and alarm criticality
                if rx_in_spec and tx_in_spec and gap_ok and not alarm_critical:
                    next_step_id = 'SS_WIFI_OR_WIRED'
                else:
                    next_step_id = 'SS_LIGHT_VALIDATE'
                    
            except ValueError:
                # Invalid numbers, let user proceed to validation step
                next_step_id = 'SS_LIGHT_VALIDATE'
    
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
    
    # Update case information based on step (but don't overwrite equipment data)
    if current_step_id == 'ROUTER_CHECK' and not case.router_type:
        case.router_type = action_taken
    elif current_step_id == 'ISSUE_TYPE':
        case.issue_type = action_taken
    # NOTE: Removed ont_type overwrite to preserve equipment selection
    
    # Update session
    step_history = session.get('step_history', [])
    step_history.append({
        'step_id': current_step_id,
        'action': action_taken,
        'timestamp': datetime.now().isoformat()
    })
    session['step_history'] = step_history
    session['current_step'] = next_step_id
    
    # Check if this is an end step or escalation
    if next_step_id == 'ESCALATED':
        # Generate Tier 2 escalation report
        case.status = 'escalated'
        case.resolution = 'Escalated to Tier 2'
        case.end_time = datetime.now().timestamp()
        case.completed_at = datetime.utcnow()
        
        # Store escalation data for report generation
        session['escalation_data'] = input_data
        
        db.session.commit()
        
        flash('Case escalated to Tier 2. Generating escalation report...', 'info')
        return redirect(url_for('case_summary', case_id=case.id))
    
    # Check if this is a dispatch or escalation step
    if next_step_id == 'DISPATCH_SUMMARY':
        # Generate dispatch report
        case.status = 'dispatch_pending'
        case.resolution = 'Hardware dispatch required'
        case.end_time = datetime.now().timestamp()
        case.completed_at = datetime.utcnow()
        
        # Store dispatch data for report generation
        session['dispatch_data'] = input_data
        
        db.session.commit()
        
        flash('Dispatch ticket created. Generating dispatch report...', 'info')
        return redirect(url_for('case_summary', case_id=case.id))
    
    elif next_step_id == 'ESCALATION_SUMMARY':
        # Generate escalation report
        case.status = 'escalated'
        case.resolution = 'Escalated to Tier 2'
        case.end_time = datetime.now().timestamp()
        case.completed_at = datetime.utcnow()
        
        # Store escalation data for report generation
        session['escalation_data'] = input_data
        
        db.session.commit()
        
        flash('Case escalated to Tier 2. Generating escalation report...', 'info')
        return redirect(url_for('case_summary', case_id=case.id))
    
    elif next_step_id == 'CASE_COMPLETED':
        # Case is completed
        case.status = 'completed'
        case.end_time = datetime.now().timestamp()
        case.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Case completed successfully!', 'success')
        return redirect(url_for('case_summary', case_id=case.id))
    
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
    
    # Check if this is an escalated case that needs Tier 2 report
    escalation_report = None
    if case.status == 'escalated':
        escalation_report = generate_tier2_escalation_report(case)
    
    # Check if this is a dispatch case that needs dispatch report
    dispatch_report = None
    if case.status in ['dispatch_pending', 'resolved'] and (
        any(step.step_id.startswith('DISPATCH_') for step in case.steps) or
        case.issue_type == 'Complete Outage'
    ):
        dispatch_report = generate_dispatch_report(case)
    
    return render_template('case_summary.html', case=case, dispatch_report=dispatch_report, escalation_report=escalation_report)

@app.route('/dispatch_report/<int:case_id>')
def dispatch_report(case_id):
    case = TroubleshootingCase.query.get_or_404(case_id)
    report = generate_dispatch_report(case)
    return render_template('dispatch_report.html', case=case, report=report)

def generate_dispatch_report(case):
    """Generate comprehensive dispatch report for field service"""
    customer_info = case.get_customer_info()
    
    # Collect all troubleshooting data from steps
    troubleshooting_data = {}
    ont_light_status = ""
    alarm_details = ""
    steps_taken = []
    
    for step in case.steps:
        # Collect step descriptions for steps taken
        if step.action_taken:
            steps_taken.append(step.action_taken)
        if step.result:
            steps_taken.append(f"Result: {step.result}")
            
        if step.notes:
            lines = step.notes.split('\n')
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    troubleshooting_data[key.strip()] = value.strip()
        
        # Capture specific data based on step ID
        if step.step_id == 'START':
            ont_light_status = step.notes or ""
        elif 'ALARM' in step.step_id:
            alarm_details = step.notes or ""
    
    # Extract specific fields from troubleshooting data
    account_number = customer_info.get('account', 'N/A')
    hub_name = troubleshooting_data.get('hub_name', troubleshooting_data.get('location', 'N/A'))
    ont_id = troubleshooting_data.get('ont_id', case.ont_id or 'N/A')
    router_id = troubleshooting_data.get('router_id', case.router_id or 'N/A')
    speed_package = troubleshooting_data.get('speed_package', troubleshooting_data.get('service_tier', 'N/A'))
    reported_issue = case.issue_type or 'Complete Outage'
    alarms_reported = troubleshooting_data.get('alarm_type', alarm_details or 'None reported')
    light_levels = troubleshooting_data.get('rx_levels', troubleshooting_data.get('ont_rx_power', 'N/A'))
    l2_user_aligned = troubleshooting_data.get('l2_user_aligned', 'N/A')
    equipment_rebooted = 'YES' if any('reboot' in step.lower() for step in steps_taken) else 'N/A'
    connections_verified = 'YES' if any('connection' in step.lower() or 'cable' in step.lower() for step in steps_taken) else 'N/A'
    time_frame = troubleshooting_data.get('issue_time_frame', troubleshooting_data.get('when_started', 'N/A'))
    agent_initials = troubleshooting_data.get('agent_initials', 'N/A')
    
    # Extract additional technical details
    rx_olt = troubleshooting_data.get('rx_olt', troubleshooting_data.get('olt_rx_power', 'N/A'))
    rx_ont = troubleshooting_data.get('rx_ont', troubleshooting_data.get('ont_rx_power', light_levels))
    rx_delta = troubleshooting_data.get('rx_delta', 'N/A')
    ont_led_status = troubleshooting_data.get('ont_led_status', troubleshooting_data.get('ont_lights', 'N/A'))
    router_led_status = troubleshooting_data.get('router_led_status', troubleshooting_data.get('router_lights', 'N/A'))
    ont_rebooted = 'YES' if any('ont' in step.lower() and 'reboot' in step.lower() for step in steps_taken) else 'NO'
    router_rebooted = 'YES' if any('router' in step.lower() and 'reboot' in step.lower() for step in steps_taken) else 'NO'
    cable_checked = connections_verified
    resolved = 'NO' if case.status == 'dispatch_pending' else 'YES'
    dispatch_required = 'YES' if case.status == 'dispatch_pending' else 'NO'
    escalate_tier2 = 'YES' if case.status == 'escalated' else 'NO'
    
    # Format steps taken properly
    formatted_steps = []
    for i, step in enumerate(steps_taken[:4], 1):
        formatted_steps.append(f"• {step}")
    
    while len(formatted_steps) < 4:
        formatted_steps.append("• N/A")

    # Create copy-pastable formatted report matching the exact format requested
    formatted_report = f"""──────────────────────  HARD-DOWN TROUBLESHOOTING REPORT  ──────────────────────
Account #:          {account_number}
Hub / Node:         {hub_name}
Speed Package:      {speed_package}

ONT ID / Serial:    {ont_id}
Router ID (MAC):    {router_id}
L2 User Aligned:    {l2_user_aligned}

Reported Issue:     NO INTERNET (Hard Down)
Customer Timeframe: {time_frame}

▼ LIGHT / SIGNAL READINGS
  • Rx @ OLT:       {rx_olt} dBm
  • Rx @ ONT:       {rx_ont} dBm
  • Delta:          {rx_delta} dB
  • ONT LEDs:       {ont_led_status}
  • Router LED:     {router_led_status}

▼ ACTIVE ALARMS (AltiPlano / CMS)
{alarms_reported}

▼ STEPS TAKEN
{formatted_steps[0]}
{formatted_steps[1]}
{formatted_steps[2]}
{formatted_steps[3] if len(formatted_steps) > 3 else '• Additional troubleshooting completed'}

Equipment Rebooted:         ONT {ont_rebooted}   |   Router {router_rebooted}
Connections Physically Checked:  {cable_checked}

▼ OUTCOME
Resolved?            {resolved}
Dispatch Required?   {dispatch_required}   (Ticket #: ____________)
Escalated to Tier 2? {escalate_tier2}   (Reason: ______________)

Agent Initials:      {agent_initials}
Date/Time Submitted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
──────────────────────────────────────────────────────────────────────────────────"""
    
    # Also return structured data for template use
    report = {
        'case_number': case.case_number,
        'account_number': account_number,
        'hub_name': hub_name,
        'ont_id': ont_id,
        'router_id': router_id,
        'speed_package': speed_package,
        'reported_issue': reported_issue,
        'steps_taken': ' | '.join(steps_taken) if steps_taken else 'Standard troubleshooting completed',
        'alarms_reported': alarms_reported,
        'light_levels': light_levels,
        'l2_user_aligned': l2_user_aligned,
        'equipment_rebooted': equipment_rebooted,
        'connections_verified': connections_verified,
        'time_frame': time_frame,
        'agent_initials': agent_initials,
        'formatted_report': formatted_report,
        'customer_name': customer_info.get('name', 'N/A'),
        'phone_number': customer_info.get('phone', 'N/A'),
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'rx_olt': rx_olt,
        'rx_ont': rx_ont,
        'rx_delta': rx_delta,
        'ont_led_status': ont_led_status,
        'router_led_status': router_led_status,
        'ont_rebooted': ont_rebooted,
        'router_rebooted': router_rebooted,
        'cable_checked': cable_checked,
        'resolved': resolved,
        'dispatch_required': dispatch_required,
        'escalate_tier2': escalate_tier2
    }
    
    return report

def generate_tier2_escalation_report(case):
    """Generate comprehensive Tier 2 escalation report"""
    escalation_data = session.get('escalation_data', {})
    customer_info = case.get_customer_info()
    
    # Collect key diagnostic information and steps taken
    light_levels = []
    alarms_found = []
    speeds_tested = []
    steps_taken = []
    
    for step in case.steps:
        if step.step_id != 'NOTE':
            # Extract light levels
            if 'ont_rx_power' in step.notes or 'olt_tx_power' in step.notes:
                lines = step.notes.split('\n')
                for line in lines:
                    if 'ont_rx_power:' in line.lower() or 'olt_tx_power:' in line.lower():
                        light_levels.append(line.strip())
            
            # Extract alarms
            if 'alarm' in step.notes.lower():
                lines = step.notes.split('\n')
                for line in lines:
                    if 'alarm' in line.lower() and ':' in line:
                        alarms_found.append(line.strip())
            
            # Extract speed tests
            if 'speed' in step.notes.lower() or 'mbps' in step.notes.lower():
                lines = step.notes.split('\n')
                for line in lines:
                    if 'speed' in line.lower() and ('mbps' in line.lower() or 'gbps' in line.lower()):
                        speeds_tested.append(line.strip())
            
            # Simplified step summary
            if step.action_taken:
                action = step.action_taken
                # Clean up verbose instructions
                if len(action) > 80:
                    action = action[:80] + "..."
                steps_taken.append(f"{step.step_id}: {action}")
            else:
                steps_taken.append(step.step_id)
    
    report = {
        'case_number': case.case_number,
        'escalation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'tier1_agent': 'Tier 1 Support',
        'escalation_reason': escalation_data.get('escalation_reason', 'N/A'),
        'priority_level': escalation_data.get('priority_level', 'medium'),
        
        # Customer Information
        'customer_name': customer_info.get('name', 'N/A'),
        'customer_phone': customer_info.get('phone', 'N/A'),
        'customer_email': customer_info.get('email', 'N/A'),
        'customer_address': customer_info.get('address', 'N/A'),
        'customer_availability': escalation_data.get('customer_availability', 'N/A'),
        
        # Equipment Information
        'ont_type': case.ont_type or 'N/A',
        'ont_id': case.ont_id or 'N/A',
        'router_type': case.router_type or 'N/A',
        'router_id': case.router_id or 'N/A',
        
        # Issue Details
        'reported_issue': case.issue_type or 'N/A',
        'current_speeds': escalation_data.get('current_speeds', 'N/A'),
        'expected_speeds': customer_info.get('speed_plan', 'N/A'),
        
        # Diagnostic Information
        'light_levels': light_levels,
        'alarms_found': alarms_found,
        'speeds_tested': speeds_tested,
        'steps_taken': steps_taken,
        'total_steps': len(steps_taken),
        'case_duration': case.get_duration(),
        'case_start_time': case.created_at.strftime('%Y-%m-%d %H:%M:%S') if case.created_at else 'N/A'
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

@app.route('/recover_session')
def recover_session():
    # Find the most recent active case and redirect to it
    recent_case = TroubleshootingCase.query.filter_by(status='in_progress').order_by(TroubleshootingCase.created_at.desc()).first()
    if recent_case:
        session['case_id'] = recent_case.id
        flash('Your troubleshooting case has been recovered!', 'success')
        return redirect(url_for('troubleshoot_wizard', case_id=recent_case.id))
    else:
        flash('No active cases found. Starting fresh.', 'info')
        return redirect(url_for('index'))

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    """Handle one-click feedback submission"""
    data = request.get_json()
    case_id = data.get('case_id')
    rating = data.get('rating')
    comments = data.get('comments', '')
    
    if not case_id or not rating:
        return jsonify({'success': False, 'message': 'Missing required fields'})
    
    # Verify case exists
    case = TroubleshootingCase.query.get(case_id)
    if not case:
        return jsonify({'success': False, 'message': 'Case not found'})
    
    # Check if feedback already exists for this case
    existing_feedback = CaseFeedback.query.filter_by(case_id=case_id).first()
    if existing_feedback:
        # Update existing feedback
        existing_feedback.rating = rating
        existing_feedback.comments = comments
        existing_feedback.submitted_at = datetime.utcnow()
    else:
        # Create new feedback
        feedback = CaseFeedback(
            case_id=case_id,
            rating=rating,
            comments=comments
        )
        db.session.add(feedback)
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Feedback submitted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error saving feedback'})
