"""
Audit trail for tracking all edits made to allocations
"""
import json
import os
from datetime import datetime
import sys


class AuditTrail:
    """Track all changes made to allocations for traceability"""
    
    def __init__(self):
        self.history_file = self.get_history_file_path()
    
    def get_history_file_path(self):
        """Get path for audit history file"""
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        return os.path.join(base_path, "audit_trail.json")
    
    def log_edit(self, change_type, allocation_date, shift_time, details, user="Admin"):
        """
        Log an edit to the audit trail
        
        Args:
            change_type: Type of change made
                - 'ALLOCATION_CREATED' - New allocation created
                - 'ALLOCATION_EDITED' - Existing allocation modified
                - 'WORKER_ADDED' - Worker added to allocation
                - 'WORKER_REMOVED' - Worker removed from allocation
                - 'ALLOCATION_DELETED' - Entire allocation deleted
                - 'PRODUCT_CHANGED' - Product assignment changed
                - 'LOT_NUMBER_CHANGED' - Lot number changed
            allocation_date: Date of allocation (YYYY-MM-DD)
            shift_time: Morning/Evening
            details: Dictionary with specific change details
            user: Username who made the change
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        audit_entry = {
            'id': self.generate_entry_id(),
            'timestamp': timestamp,
            'change_type': change_type,
            'allocation_date': allocation_date,
            'shift_time': shift_time,
            'user': user,
            'details': details
        }
        
        # Load existing audit trail
        audit_log = self.load_audit_log()
        
        # Add new entry
        audit_log.append(audit_entry)
        
        # Save back
        self.save_audit_log(audit_log)
        
        print(f"[AUDIT] {timestamp} - {change_type}: {allocation_date} {shift_time}")
        return audit_entry['id']
    
    def generate_entry_id(self):
        """Generate unique ID for audit entry"""
        return datetime.now().strftime("%Y%m%d%H%M%S%f")
    
    def load_audit_log(self):
        """Load audit trail from file"""
        if not os.path.exists(self.history_file):
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading audit trail: {e}")
            return []
    
    def save_audit_log(self, audit_log):
        """Save audit trail to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(audit_log, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving audit trail: {e}")
    
    def get_allocation_audit_log(self, allocation_date, shift_time):
        """Get all audit entries for a specific allocation"""
        audit_log = self.load_audit_log()
        return [
            entry for entry in audit_log
            if entry['allocation_date'] == allocation_date 
            and entry['shift_time'] == shift_time
        ]
    
    def get_recent_changes(self, limit=100):
        """Get recent changes across all allocations"""
        audit_log = self.load_audit_log()
        return audit_log[-limit:] if len(audit_log) > limit else audit_log
    
    def get_changes_by_date_range(self, start_date, end_date):
        """Get all changes within a date range"""
        audit_log = self.load_audit_log()
        
        filtered = []
        for entry in audit_log:
            entry_date = entry['allocation_date']
            if start_date <= entry_date <= end_date:
                filtered.append(entry)
        
        return filtered
    
    def export_audit_report(self, output_file=None):
        """Export audit trail to a readable text file"""
        if output_file is None:
            output_file = os.path.join(
                os.path.dirname(self.history_file),
                f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
        
        audit_log = self.load_audit_log()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("ALLOCATION SYSTEM AUDIT TRAIL REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Entries: {len(audit_log)}\n")
            f.write("=" * 80 + "\n\n")
            
            for entry in audit_log:
                f.write(f"Entry ID: {entry['id']}\n")
                f.write(f"Timestamp: {entry['timestamp']}\n")
                f.write(f"Change Type: {entry['change_type']}\n")
                f.write(f"Allocation: {entry['allocation_date']} - {entry['shift_time']}\n")
                f.write(f"User: {entry['user']}\n")
                f.write(f"Details:\n")
                
                for key, value in entry['details'].items():
                    f.write(f"  {key}: {value}\n")
                
                f.write("-" * 80 + "\n\n")
        
        return output_file


# Global instance
audit_trail = AuditTrail()