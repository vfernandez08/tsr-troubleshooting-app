from app import db
from datetime import datetime
import json

class TroubleshootingCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    case_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_info = db.Column(db.Text)  # JSON string
    ont_type = db.Column(db.String(50))
    ont_id = db.Column(db.String(50))  # ONT identifier (flexible format)
    router_type = db.Column(db.String(50))
    router_id = db.Column(db.String(50))  # Router identifier (flexible format)
    issue_type = db.Column(db.String(100))
    resolution = db.Column(db.String(200))
    status = db.Column(db.String(20), default='in_progress')  # in_progress, resolved, escalated, unresolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    start_time = db.Column(db.Float)  # timestamp
    end_time = db.Column(db.Float)  # timestamp
    
    def get_customer_info(self):
        if self.customer_info:
            return json.loads(self.customer_info)
        return {}
    
    def set_customer_info(self, info_dict):
        self.customer_info = json.dumps(info_dict)
    
    def get_duration(self):
        if self.start_time and self.end_time:
            return int(self.end_time - self.start_time)
        elif self.start_time:
            return int(datetime.now().timestamp() - self.start_time)
        return 0

class TroubleshootingStep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('troubleshooting_case.id'), nullable=False)
    step_id = db.Column(db.String(50), nullable=False)
    step_name = db.Column(db.String(200))
    action_taken = db.Column(db.String(500))
    result = db.Column(db.String(500))
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    case = db.relationship('TroubleshootingCase', backref=db.backref('steps', lazy=True, order_by='TroubleshootingStep.timestamp'))
