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
    
    return redirect(url_for('troubleshoot_wizard') + f'?case_id={case.id}')

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
    
    # Start with ONT selection (Step 1) if no ONT type is set
    if not case.ont_type:
        session['current_step'] = 'ONT_SELECTION'
        return render_template('troubleshoot_wizard.html', 
                             case=case, 
                             step='ont_selection',
                             step_title='Step 1: Select ONT Type',
                             current_step=1)
    
    # Then router selection (Step 2) if no router type is set
    elif not case.router_type:
        session['current_step'] = 'ROUTER_SELECTION'
        return render_template('troubleshoot_wizard.html', 
                             case=case, 
                             step='router_selection',
                             step_title='Step 2: Select Router Type',
                             current_step=2)
    
    # Then issue type selection (Step 3) if no issue type is set
    elif not case.issue_type:
        session['current_step'] = 'ISSUE_SELECTION'
        return render_template('troubleshoot_wizard.html', 
                             case=case, 
                             step='issue_selection',
                             step_title='Step 3: Select Issue Type',
                             current_step=3)
    
    # Finally redirect based on issue type
    else:
        # For slow speeds or intermittent issues, go to fiber pre-check first
        if case.issue_type in ['Slow Speeds', 'Intermittent Connection']:
            # For slow speeds/intermittent, skip to speed test documentation after collecting fiber data
            session['current_step'] = 'SS_START'
            session['step_history'] = []
            return redirect(url_for('troubleshoot'))
        else:
            # For hard down issues, go straight to troubleshooting
            session['current_step'] = 'START'
            session['step_history'] = []
            return redirect(url_for('troubleshoot'))

@app.route('/troubleshoot_wizard', methods=['POST'])
def troubleshoot_wizard_post():
    case_id = request.args.get('case_id') or session.get('case_id')
    case = TroubleshootingCase.query.get_or_404(case_id)
    
    # Handle ONT selection
    if 'ont_type' in request.form:
        case.ont_type = request.form['ont_type']
        case.ont_id = request.form.get('ont_id', '')
        db.session.commit()
        return redirect(url_for('troubleshoot_wizard', case_id=case_id))
    
    # Handle Router selection
    elif 'router_type' in request.form:
        case.router_type = request.form['router_type']
        case.router_id = request.form.get('router_id', '')
        db.session.commit()
        return redirect(url_for('troubleshoot_wizard', case_id=case_id))
    
    # Handle Issue Type selection
    elif 'issue_type' in request.form:
        case.issue_type = request.form['issue_type']
        db.session.commit()
        return redirect(url_for('troubleshoot_wizard', case_id=case_id))
    
    # Handle Fiber Pre-Check completion
    elif 'complete_precheck' in request.form:
        # Store pre-check data in session for troubleshooting use
        session['precheck_data'] = {
            'ont_lights': request.form.get('ont_lights'),
            'light_levels': request.form.get('light_levels'),
            'learned_address': request.form.get('learned_address'),
            'precheck_notes': request.form.get('precheck_notes')
        }
        
        # Create a pre-check step record
        step = TroubleshootingStep(
            case_id=case_id,
            step_id='PRECHECK',
            step_name='Fiber Pre-Check',
            action_taken=f"ONT Lights: {request.form.get('ont_lights')} | Light Levels: {request.form.get('light_levels', 'N/A')}",
            result=f"Learned Address: {request.form.get('learned_address', 'N/A')}",
            notes=request.form.get('precheck_notes', '')
        )
        db.session.add(step)
        db.session.commit()
        
        # Now redirect to appropriate troubleshooting step based on issue type
        if case.issue_type == 'Slow Speeds':
            # For slow speeds, skip the redundant ONT check and go to speed test documentation
            session['current_step'] = 'SS_START'
            session['step_history'] = []
        elif case.issue_type == 'Intermittent Connection':
            # For intermittent issues, also skip ONT check since we have that data
            session['current_step'] = 'SS_START'
            session['step_history'] = []
        else:
            # For other issues, use standard flow
            session['current_step'] = 'START'
            session['step_history'] = []
        return redirect(url_for('troubleshoot'))
    
    return redirect(url_for('troubleshoot_wizard', case_id=case_id))

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
    
    # Generate Tier 2 escalation report if needed
    escalation_report = None
    if current_step_id == 'TIER2_ESCALATION_SUMMARY':
        escalation_report = generate_tier2_escalation_report(case)
    
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
                         step_number=len(step_history) + 1,
                         escalation_report=escalation_report)

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
    # AI recommendations disabled for streamlined workflow
    
    # Smart validation for slow speeds light levels
    if current_step_id == 'SS_START' and input_data:
        light_levels = input_data.get('light_levels', '')
        alarm_type_1 = input_data.get('alarm_type_1', '')
        alarm_status_1 = input_data.get('alarm_status_1', '')
        
        # Route based on light level selection and alarm status
        if light_levels:
            # Determine criticality based on alarm type
            critical_alarms = ['ONU Loss of PHY Layer', 'Loss of Signal (LOS)']
            alarm_critical = alarm_type_1 in critical_alarms and alarm_status_1 == 'Active'
            
            # Check if light levels are good
            light_levels_good = light_levels.startswith('Good (-20 to -10)')
            light_levels_problem = light_levels.startswith('Low (-25 or lower)') or light_levels.startswith('Gap Too Wide')
            
            # Store validation results in session for next step
            session['light_validation'] = {
                'light_levels': light_levels,
                'light_levels_good': light_levels_good,
                'light_levels_problem': light_levels_problem,
                'alarm_type': alarm_type_1,
                'alarm_status': alarm_status_1,
                'alarm_critical': alarm_critical,
                'overall_ok': light_levels_good and not alarm_critical
            }
            
            # Auto-route based on light levels and alarm criticality
            if light_levels_good and not alarm_critical:
                # Good light levels and no critical alarms - proceed to SSID comparison
                next_step_id = 'SS_WIFI_OR_WIRED'
            elif light_levels == 'Cannot Access':
                # Cannot access light levels - go to validation for manual checking
                next_step_id = 'SS_LIGHT_VALIDATE'
            else:
                # Poor light levels or critical alarms - needs validation/escalation
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
    
    # Collect all troubleshooting data from steps with improved parsing
    diagnostic_data = {}
    troubleshooting_steps = []
    speed_data = {}
    wifi_data = {}
    event_stream_data = {}
    fiber_diagnostics = {}
    
    for step in case.steps:
        if step.step_id != 'NOTE':
            # Parse notes to extract structured data with better key matching
            if step.notes:
                lines = step.notes.split('\n')
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Store original key for better matching
                        diagnostic_data[key] = value
                        
                        # Categorize data by original key names
                        key_lower = key.lower()
                        if any(term in key_lower for term in ['speed', 'mbps', 'download', 'upload', 'device']):
                            speed_data[key] = value
                        elif any(term in key_lower for term in ['wifi', 'channel', 'utilization', 'ghz', 'band']):
                            wifi_data[key] = value
                        elif any(term in key_lower for term in ['event', 'stream', 'selected']):
                            event_stream_data[key] = value
                        elif any(term in key_lower for term in ['light', 'rx', 'tx', 'power', 'alarm']):
                            fiber_diagnostics[key] = value
            
            # Add step description with more detail
            if step.action_taken:
                step_desc = step.action_taken
                if step.result:
                    step_desc += f" → {step.result}"
                elif step.notes and len(step.notes.split('\n')) == 1:
                    step_desc += f" → {step.notes}"
                troubleshooting_steps.append(step_desc)
    
    # Extract key information with better fallbacks from actual form data
    account_number = customer_info.get('account', diagnostic_data.get('Account Number', diagnostic_data.get('account_number', 'N/A')))
    
    # Get contact info from escalation data first, then diagnostic data
    contact_number = (escalation_data.get('tier2_contact_number') or 
                     escalation_data.get('contact_number') or 
                     diagnostic_data.get('contact_number') or 
                     diagnostic_data.get('Contact Number') or
                     customer_info.get('phone', 'N/A'))
    
    best_time = (escalation_data.get('best_time_to_call') or 
                escalation_data.get('best_time') or 
                diagnostic_data.get('best_time_to_call') or
                diagnostic_data.get('Best Time to Call') or
                customer_info.get('best_time', 'N/A'))
    
    # Extract speed information from the actual form field names
    customer_speeds = 'N/A'
    
    # Look for specific speed test fields
    device_download = diagnostic_data.get('Customer Device Download Speed (Mbps)', diagnostic_data.get('customer_download_speed'))
    device_upload = diagnostic_data.get('Customer Device Upload Speed (Mbps)', diagnostic_data.get('customer_upload_speed'))
    device_type = diagnostic_data.get('Customer Device Used for Speed Test', diagnostic_data.get('customer_device_type', diagnostic_data.get('customer_device')))
    
    eero_download = diagnostic_data.get('Eero Analytics Download Speed (Mbps)', diagnostic_data.get('eero_analytics_download'))
    eero_upload = diagnostic_data.get('Eero Analytics Upload Speed (Mbps)', diagnostic_data.get('eero_analytics_upload'))
    
    # Build speed summary
    speed_parts = []
    if device_download and device_upload:
        speed_parts.append(f"Device: {device_download}/{device_upload} Mbps ({device_type or 'Unknown device'})")
    
    if eero_download and eero_upload:
        speed_parts.append(f"Eero: {eero_download}/{eero_upload} Mbps")
    
    if speed_parts:
        customer_speeds = " | ".join(speed_parts)
    else:
        # Fallback - look for any speed-related data
        for key, value in diagnostic_data.items():
            if 'speed' in key.lower() and 'mbps' in str(value).lower():
                customer_speeds = f"{key}: {value}"
                break
    
    # Extract expected speed/package information
    expected_speed = (diagnostic_data.get("Customer's Speed Plan") or 
                     diagnostic_data.get('customer_speed_plan') or
                     diagnostic_data.get('speed_package') or 
                     diagnostic_data.get('service_tier', 'N/A'))
    
    # Extract WiFi environment details from actual field names
    wifi_24_util = diagnostic_data.get('2.4 GHz Channel Utilization (%)', diagnostic_data.get('channel_utilization_2_4'))
    wifi_5_util = diagnostic_data.get('5 GHz Channel Utilization (%)', diagnostic_data.get('channel_utilization_5'))
    
    wifi_details = []
    if wifi_24_util:
        wifi_details.append(f"2.4GHz: {wifi_24_util}% utilization")
    if wifi_5_util:
        wifi_details.append(f"5GHz: {wifi_5_util}% utilization")
    
    wifi_environment = " | ".join(wifi_details) if wifi_details else "N/A"
    
    # Extract event stream findings
    selected_events = (diagnostic_data.get('Events Found in Stream (Select All That Apply)') or 
                      diagnostic_data.get('selected_events') or 'N/A')
    
    troubleshooting_attempts = (diagnostic_data.get('Troubleshooting Steps Completed (Document Each Attempt)') or 
                               diagnostic_data.get('troubleshooting_attempts') or 'N/A')
    
    # Get fiber diagnostics with better key matching
    light_levels = (diagnostic_data.get('Light Levels') or 
                   diagnostic_data.get('light_levels') or 'N/A')
    
    alarm_status = (diagnostic_data.get('Alarm Status') or 
                   diagnostic_data.get('alarm_status_1') or 'N/A')
    
    alarm_type = (diagnostic_data.get('Alarm Type') or 
                 diagnostic_data.get('alarm_type_1') or 'N/A')
    
    # Format escalation reason
    escalation_reason = escalation_data.get('escalation_reason', 'Multiple troubleshooting attempts failed')
    
    # Format case duration properly
    case_duration_minutes = case.get_duration()
    try:
        total_minutes = int(case_duration_minutes)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        duration_formatted = f"{hours:02d}:{minutes:02d}:00"
        sla_status = "✓ Within SLA" if total_minutes <= 60 else "⚠ Exceeds SLA"
    except:
        duration_formatted = f"{case_duration_minutes} minutes"
        sla_status = ""

    # Determine escalation trigger
    escalation_trigger = escalation_reason
    if "multiple" in escalation_reason.lower():
        escalation_trigger = "Multiple troubleshooting attempts failed - speeds remain below acceptable threshold"
    elif "intermittent" in escalation_reason.lower():
        escalation_trigger = "Intermittent connectivity persists after standard resolution steps"
    elif "equipment" in escalation_reason.lower():
        escalation_trigger = "Suspected equipment failure requires advanced diagnostics"

    # Format troubleshooting steps as table
    steps_table = ""
    if troubleshooting_steps:
        for i, step in enumerate(troubleshooting_steps, 1):
            # Try to split step into action and result
            if " → " in step:
                action, result = step.split(" → ", 1)
            elif "Result:" in step:
                parts = step.split("Result:", 1)
                action = parts[0].strip()
                result = parts[1].strip() if len(parts) > 1 else "Completed"
            else:
                action = step
                result = "Completed"
            steps_table += f"| {action} | {result} |\n"
        
        # Add escalation trigger row
        steps_table += f"| — | — |\n"
        steps_table += f"| **Escalation Trigger** | {escalation_trigger} |\n"
    else:
        steps_table = "| Standard troubleshooting workflow | Completed per procedure |\n"
        steps_table += f"| — | — |\n"
        steps_table += f"| **Escalation Trigger** | {escalation_trigger} |\n"

    # Create formatted report with comprehensive data
    formatted_report = f"""### TIER 2 ESCALATION – {case.issue_type or 'Technical Issue'}
**Case:** {case.case_number}  **Raised:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} CST

| Customer | Value |
|----------|-------|
| Account # | {account_number} |
| Phone | {contact_number if contact_number != 'N/A' else '⚠ NOT CAPTURED'} |
| Best Time | {best_time if best_time != 'N/A' else '(not specified)'} |
| Issue Type | {case.issue_type or 'Not specified'} |

---

| Equipment | Details |
|-----------|---------|
| ONT | {case.ont_type or 'Not specified'}{f' ({case.ont_id})' if case.ont_id and case.ont_id != 'N/A' else ''} |
| Light Levels | {light_levels if light_levels != 'N/A' else '(not captured)'} |
| Router | {case.router_type or 'Not specified'}{f' ({case.router_id})' if case.router_id and case.router_id != 'N/A' else ''} |
| Alarms | {alarm_type if alarm_type != 'N/A' else 'None reported'} - {alarm_status if alarm_status != 'N/A' else 'Status unknown'} |

---

**Speed Performance & WiFi Environment**

| Test Type | Result | Expected |
|-----------|--------|----------|
| Customer Reported | {customer_speeds if customer_speeds != 'N/A' else '⚠ NOT TESTED'} | {expected_speed if expected_speed != 'N/A' else 'Unknown package'} |
| WiFi Environment | {wifi_environment} | Normal: <80% utilization |

---

**Event Stream Analysis**
```
Selected Events: {selected_events if selected_events != 'N/A' else 'None documented'}
```

**Detailed Troubleshooting Attempts**
```
{troubleshooting_attempts if troubleshooting_attempts != 'N/A' else 'Standard troubleshooting workflow completed'}
```

---

**Tier 1 Actions Summary**

| Step | Result |
|------|--------|
{steps_table}

Tier 1 Handling Time: {duration_formatted} {f'({sla_status})' if sla_status else ''}

---

**Current Status**  
Issue persists after comprehensive Tier 1 troubleshooting. Customer ready for Tier 2 contact.

**⚠ CRITICAL INFO FOR TIER 2:**
- Contact Number: {contact_number if contact_number != 'N/A' else 'MISSING - Use account lookup'}
- Best Contact Time: {best_time if best_time != 'N/A' else 'Standard business hours'}
- Issue Duration: {case_duration_minutes} minutes
- Escalation Reason: {escalation_trigger}

**Suggested Next Steps**  
1. Advanced network diagnostics required
2. Review WiFi channel utilization and event stream findings
3. Analyze speed performance gap between device and Eero analytics
4. Contact customer using information above

*Generated by Tier 1 Support | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"""
    
    # Return both formatted report and structured data
    report = {
        'case_number': case.case_number,
        'escalation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'tier1_agent': 'Tier 1 Support',
        'escalation_reason': escalation_reason,
        'priority_level': escalation_data.get('priority_level', 'medium'),
        
        # Customer Information
        'contact_number': contact_number,
        'best_time': best_time,
        'account_number': account_number,
        'customer_availability': escalation_data.get('customer_availability', 'N/A'),
        
        # Equipment Information
        'ont_type': case.ont_type or 'N/A',
        'ont_id': case.ont_id or 'N/A',
        'router_type': case.router_type or 'N/A',
        'router_id': case.router_id or 'N/A',
        
        # Issue Details
        'reported_issue': case.issue_type or 'N/A',
        'current_speeds': customer_speeds,
        'expected_speeds': expected_speed,
        
        # Diagnostic Information
        'light_levels': light_levels,
        'alarm_status': alarm_status,
        'alarm_type': alarm_type,
        'troubleshooting_steps': troubleshooting_steps,
        'total_steps': len(troubleshooting_steps),
        'case_duration': case.get_duration(),
        'case_start_time': case.created_at.strftime('%Y-%m-%d %H:%M:%S') if case.created_at else 'N/A',
        
        # New detailed troubleshooting data
        'speed_data': speed_data,
        'wifi_data': wifi_data,
        'wifi_environment': wifi_environment,
        'event_stream_data': event_stream_data,
        'selected_events': selected_events,
        'troubleshooting_attempts': troubleshooting_attempts,
        'all_diagnostic_data': diagnostic_data,
        
        'formatted_report': formatted_report
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
