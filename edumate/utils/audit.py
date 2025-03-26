import json
import os
from datetime import datetime
from .logger import log_audit

class AuditTrail:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.audit_file = os.path.join(data_dir, 'audit_trail.json')
        self.load_audit_trail()

    def load_audit_trail(self):
        """Load or initialize audit trail"""
        if os.path.exists(self.audit_file):
            with open(self.audit_file, 'r') as f:
                self.audit_data = json.load(f)
        else:
            self.audit_data = []
            self.save_audit_trail()

    def save_audit_trail(self):
        """Save audit trail to file"""
        with open(self.audit_file, 'w') as f:
            json.dump(self.audit_data, f, indent=4)

    def add_entry(self, user_id, action, details):
        """Add a new audit trail entry"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': action,
            'details': details,
            'ip_address': details.get('ip_address', 'unknown')
        }
        
        self.audit_data.append(entry)
        self.save_audit_trail()
        log_audit(user_id, action, json.dumps(details))

    def get_user_actions(self, user_id, start_date=None, end_date=None):
        """Get all actions performed by a user within a date range"""
        actions = [entry for entry in self.audit_data if entry['user_id'] == user_id]
        
        if start_date:
            actions = [a for a in actions if a['timestamp'] >= start_date.isoformat()]
        if end_date:
            actions = [a for a in actions if a['timestamp'] <= end_date.isoformat()]
        
        return actions

    def get_action_history(self, action_type, start_date=None, end_date=None):
        """Get history of a specific type of action"""
        actions = [entry for entry in self.audit_data if entry['action'] == action_type]
        
        if start_date:
            actions = [a for a in actions if a['timestamp'] >= start_date.isoformat()]
        if end_date:
            actions = [a for a in actions if a['timestamp'] <= end_date.isoformat()]
        
        return actions
