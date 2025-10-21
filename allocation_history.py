"""
Manage allocation history for fair worker distribution
"""
import os
import json
from datetime import datetime, timedelta
from data import get_process_group

class AllocationHistory:
    """Track and manage worker allocation history"""
    
    def __init__(self):
        self.history_file = os.path.join(os.path.dirname(__file__), "allocation_history.json")
        self.history = self.load_history()
    
    def load_history(self):
        """Load allocation history from JSON file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_history(self):
        """Save allocation history to JSON file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def add_allocation(self, process_name, worker_name, date=None):
        """Record a worker allocation - uses process GROUP not individual name"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Use group name instead of individual process name
        group_name = get_process_group(process_name)
        
        if group_name not in self.history:
            self.history[group_name] = {}
        
        if worker_name not in self.history[group_name]:
            self.history[group_name][worker_name] = []
        
        if date not in self.history[group_name][worker_name]:
            self.history[group_name][worker_name].append(date)
        
        self.save_history()
    
    def get_allocation_count(self, process_name, worker_name, days=30):
        """Get allocation count using process GROUP"""
        group_name = get_process_group(process_name)
        
        if group_name not in self.history:
            return 0
        
        if worker_name not in self.history[group_name]:
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        count = 0
        for date_str in self.history[group_name][worker_name]:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                if date >= cutoff_date:
                    count += 1
            except:
                continue
        
        return count
    
    def calculate_frequency_penalty(self, process_name, worker_name, days=30):
        """Calculate penalty using process GROUP - max penalty of 3"""
        count = self.get_allocation_count(process_name, worker_name, days)
        
        # Penalty increases with frequency, capped at 3
        if count >= 5:
            return 3  # Maximum penalty
        elif count >= 3:
            return 2
        elif count >= 1:
            return 1
        else:
            return 0

  
    def get_worker_stats(self, worker_name, days=30):
        """
        Get allocation statistics for a worker across all processes
        
        Args:
            worker_name: Name of the worker
            days: Number of days to look back
        
        Returns:
            Dictionary with process names and allocation counts
        """
        stats = {}
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for process_name, workers in self.history.items():
            if worker_name in workers:
                count = 0
                for date_str in workers[worker_name]:
                    try:
                        date = datetime.strptime(date_str, "%Y-%m-%d")
                        if date >= cutoff_date:
                            count += 1
                    except:
                        continue
                if count > 0:
                    stats[process_name] = count
        
        return stats
    
    def cleanup_old_records(self, days=90):
        """
        Remove allocation records older than specified days
        
        Args:
            days: Keep records from last X days
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for process_name in list(self.history.keys()):
            for worker_name in list(self.history[process_name].keys()):
                # Filter dates
                valid_dates = []
                for date_str in self.history[process_name][worker_name]:
                    try:
                        date = datetime.strptime(date_str, "%Y-%m-%d")
                        if date >= cutoff_date:
                            valid_dates.append(date_str)
                    except:
                        continue
                
                if valid_dates:
                    self.history[process_name][worker_name] = valid_dates
                else:
                    del self.history[process_name][worker_name]
            
            # Remove empty process entries
            if not self.history[process_name]:
                del self.history[process_name]
        
        self.save_history()

    def show_worker_frequency_stats(worker_name, days=30):
        """Show how many times worker did each process GROUP"""
        from data import PROCESS_GROUPS
        
        stats = {}
        for process_name in PROCESS_GROUPS.keys():
            group_name = get_process_group(process_name)
            count = allocation_history.get_allocation_count(process_name, worker_name, days)
            if count > 0:
                stats[group_name] = count
        
        print(f"\n{worker_name}'s assignments (last {days} days):")
        for group, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {group}: {count} times")

# Global instance
allocation_history = AllocationHistory()